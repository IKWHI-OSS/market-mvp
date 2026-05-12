"""
llm_load_test.py — Anthropic Haiku 4.5 부하 검증 + 시드 재생성

시나리오 1~4 (통합검증 1 + 시연 15 + 시드재생성 211 + 소규모운영 1,000) 누적 실행.
실제 호출당 비용을 누적 추적하여 한도 도달 시 즉시 중단.

- 입력 : data/mock_v2/{stores,products,merchants}.json
- 출력 : data/mock_v2/stories_llm.json (LLM 생성 결과)
- 환경 : server/.env 의 ANTHROPIC_API_KEY 사용
- 한도 : 누적 비용 ≥ COST_LIMIT_USD 이면 즉시 중단

실행:
  cd /Users/karla/Documents/market-mvp
  python3 scripts/llm_load_test.py
"""
from __future__ import annotations

import json
import random
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / "server" / ".env")

import anthropic  # noqa: E402
from anthropic import RateLimitError, APIStatusError  # noqa: E402

# ─── Config ────────────────────────────────────────────────────────────────

MODEL = "claude-haiku-4-5-20251001"
INPUT_PRICE_USD_PER_MTOK = 1.0
OUTPUT_PRICE_USD_PER_MTOK = 5.0
COST_LIMIT_USD = 4.99          # 사용자 명시 한도 — 1,227회 완수 보장용 안전 한도
TARGET_CALLS = 1227            # 시나리오 1+2+3+4 = 1+15+211+1000
INCREMENTAL_SAVE_EVERY = 50    # 50건마다 stories_llm.json 증분 저장
RESUME = True                  # OUT_PATH 가 있으면 이어서 호출 (기존 결과 보존)

DATA_DIR = ROOT / "data" / "mock_v2"
OUT_PATH = DATA_DIR / "stories_llm.json"

TONES = ["친근한", "전문적인", "정겨운"]
LENGTHS = ["short", "normal", "detailed"]
KEYWORD_SETS = [
    ["제철", "신선"],
    ["정직", "품질"],
    ["단골", "오래된"],
    ["새벽", "직송"],
    ["엄선", "직거래"],
]


def build_prompt(store_name: str, products: list[dict]) -> str:
    product_str = (
        ", ".join(p["product_name"] for p in products[:5])
        if products else "다양한 상품"
    )
    return (
        "당신은 전통시장 상인의 스토리 작가입니다.\n"
        "다음 정보를 바탕으로 고객의 마음을 끄는 따뜻한 스토리 문구를 2~3문장으로 작성하세요.\n\n"
        f"점포명: {store_name}\n"
        f"주요 판매 상품: {product_str}\n\n"
        "스토리 문구 (2~3문장, 한국어):"
    )


def _p(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def main() -> None:
    client = anthropic.Anthropic()

    stores    = json.loads((DATA_DIR / "stores.json").read_text())
    products  = json.loads((DATA_DIR / "products.json").read_text())
    merchants = json.loads((DATA_DIR / "merchants.json").read_text())

    products_by_store = {}
    for p in products:
        products_by_store.setdefault(p["store_id"], []).append(p)
    merchant_by_store = {m["store_id"]: m for m in merchants}

    # 호출 시퀀스 생성: 점포(101) × 톤(3) × 길이(3) = 909 + α
    random.seed(42)
    sequence = []
    for s in stores:
        for tone in TONES:
            for length in LENGTHS:
                sequence.append({
                    "store":    s,
                    "tone":     tone,
                    "length":   length,
                    "keywords": random.choice(KEYWORD_SETS),
                })
    # 추가 다양성 — 무작위 조합 318건
    while len(sequence) < TARGET_CALLS:
        sequence.append({
            "store":    random.choice(stores),
            "tone":     random.choice(TONES),
            "length":   random.choice(LENGTHS),
            "keywords": random.choice(KEYWORD_SETS),
        })
    random.shuffle(sequence)

    # RESUME — 기존 결과 보존하고 이어서 호출
    stories_out: list = []
    skip_n = 0
    if RESUME and OUT_PATH.exists():
        try:
            stories_out = json.loads(OUT_PATH.read_text())
            skip_n = len(stories_out)
            _p(f"[RESUME] 기존 결과 {skip_n}건 로드 — 시퀀스 첫 {skip_n}건 skip")
        except Exception as e:
            _p(f"[RESUME] 기존 결과 로드 실패: {e} — 처음부터 시작")
            stories_out = []
            skip_n = 0

    _p(f"총 호출 계획     : {len(sequence)}건")
    _p(f"이어서 호출      : {len(sequence) - skip_n}건 (skip={skip_n})")
    _p(f"비용 한도        : ${COST_LIMIT_USD:.2f}  (이번 세션 새 호출 누적)")
    _p(f"가격(Haiku 4.5) : ${INPUT_PRICE_USD_PER_MTOK}/MTok in, ${OUTPUT_PRICE_USD_PER_MTOK}/MTok out")
    _p()

    total_in = total_out = 0
    total_cost = 0.0
    calls = ok = err = rl_hits = 0
    start = time.time()
    last_log = start

    for idx, item in enumerate(sequence):
        if idx < skip_n:
            continue
        if total_cost >= COST_LIMIT_USD:
            _p(
                f"\n[STOP] 비용 한도 ${COST_LIMIT_USD:.2f} 도달 — "
                f"누적 ${total_cost:.4f}, 호출 {calls}건 후 중단"
            )
            break

        # 증분 저장 — 중단되더라도 결과 보존 (skip_n + new calls 모두 포함)
        if calls > 0 and calls % INCREMENTAL_SAVE_EVERY == 0:
            OUT_PATH.write_text(json.dumps(stories_out, ensure_ascii=False, indent=2))

        s = item["store"]
        p_list = products_by_store.get(s["store_id"], [])
        prompt = build_prompt(s["store_name"], p_list)

        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            calls += 1
            ok += 1
            u = msg.usage
            total_in  += u.input_tokens
            total_out += u.output_tokens
            total_cost = (
                total_in  * INPUT_PRICE_USD_PER_MTOK +
                total_out * OUTPUT_PRICE_USD_PER_MTOK
            ) / 1_000_000
            text = msg.content[0].text.strip()

            sel_len = item["length"]
            content_short    = (text[:60] + "...") if len(text) > 60 else text
            content_normal   = text
            content_detailed = text + " 오늘도 제철 재료와 점포만의 기준으로 정성껏 모시겠습니다."

            stories_out.append({
                "story_id":         f"lst{calls:06d}-{uuid.uuid4().hex[:12]}",
                "store_id":         s["store_id"],
                "merchant_id":      (merchant_by_store.get(s["store_id"]) or {}).get("merchant_id"),
                "title":            None,
                "content":          {"short": content_short,
                                     "normal": content_normal,
                                     "detailed": content_detailed}[sel_len],
                "content_short":    content_short,
                "content_normal":   content_normal,
                "content_detailed": content_detailed,
                "tone":             item["tone"],
                "selected_length":  sel_len,
                "hashtags_json":    json.dumps(
                    [f"#{kw}" for kw in item["keywords"]] + [f"#{s['store_name'].replace(' ', '')}"],
                    ensure_ascii=False,
                ),
                "interview_text":   None,
                "fallback_mode":    0,
                "is_published":     1 if calls % 2 == 0 else 0,
                "published_at": (
                    datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    if calls % 2 == 0 else None
                ),
                "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            })

            now = time.time()
            if calls in (1, 5, 10, 50) or calls % 100 == 0 or (now - last_log) > 30:
                elapsed = now - start
                rate = calls / elapsed if elapsed > 0 else 0
                _p(
                    f"  [{calls:4d}/{len(sequence):4d}] {s['store_name'][:16]:18s} "
                    f"tok({u.input_tokens:3d}/{u.output_tokens:3d}) "
                    f"cum=${total_cost:.4f} ({rate:.1f}/s, {elapsed:.0f}s)"
                )
                last_log = now

        except RateLimitError:
            rl_hits += 1
            err += 1
            sleep_s = min(60, 5 * rl_hits)
            _p(f"  [RL] idx={idx} — rate limited, sleeping {sleep_s}s")
            time.sleep(sleep_s)
        except APIStatusError as e:
            err += 1
            _p(f"  [API] idx={idx}: {e.status_code} {str(e)[:80]}")
            if err > 10:
                _p("  [STOP] API 에러 누적 — 중단")
                break
        except Exception as e:  # noqa: BLE001
            err += 1
            _p(f"  [ERR] idx={idx}: {type(e).__name__}: {str(e)[:80]}")
            if err > 10:
                _p("  [STOP] 일반 에러 누적 — 중단")
                break

    # 결과 저장
    OUT_PATH.write_text(json.dumps(stories_out, ensure_ascii=False, indent=2))

    elapsed = time.time() - start
    _p()
    _p("=== 완료 ===")
    _p(f"호출 결과 : 성공 {ok}건 / 에러 {err}건 (rate-limit hit {rl_hits}회)")
    _p(f"토큰 사용 : input {total_in:,} / output {total_out:,}")
    _p(f"누적 비용 : ${total_cost:.4f} ≈ ₩{total_cost*1380:.0f}")
    _p(f"한도 대비 : {total_cost / COST_LIMIT_USD * 100:.1f}% (한도 ${COST_LIMIT_USD:.2f})")
    _p(f"실행 시간 : {elapsed:.1f}초 ({ok/elapsed if elapsed>0 else 0:.2f} req/s)")
    _p(f"결과 파일 : {OUT_PATH} ({len(stories_out)}건)")


if __name__ == "__main__":
    sys.exit(main() or 0)
