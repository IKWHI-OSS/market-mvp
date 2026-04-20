"""
validate_docs.py — MySQL INFORMATION_SCHEMA vs db_setup_report.md 불일치 검증

비교 대상:
  - 섹션 3 (엔터티별 데이터 현황): 테이블 목록 존재 여부
  - 섹션 5 (주요 필드 정의 요약): PK 컬럼, FK 관계, ENUM 값, 주요 컬럼 존재 여부

검증 항목:
  C1. 테이블 목록 일치 여부 (섹션 3 ↔ DB)
  C2. PK 컬럼 일치 여부    (섹션 5 ↔ DB PRIMARY KEY)
  C3. FK 관계 일치 여부    (섹션 5 ↔ DB FOREIGN KEY)
  C4. ENUM 값 일치 여부    (섹션 5 ↔ DB COLUMN_TYPE)
  C5. 주요 컬럼 존재 여부  (섹션 5 ↔ DB 컬럼 목록)
"""

import os
import re
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# .env 로드
# ──────────────────────────────────────────────────────────────

def _load_dotenv() -> None:
    for candidate in [Path(".env"), Path(__file__).parent.parent / ".env"]:
        if not candidate.exists():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        break


_load_dotenv()

try:
    import mysql.connector
except ImportError:
    sys.exit("[ERROR] mysql-connector-python 이 설치되지 않았습니다.\n"
             "  pip install mysql-connector-python")

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "127.0.0.1"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": "market_mvp",
}

REPORT_PATH = Path(__file__).parent.parent / "docs" / "db_setup_report.md"

# ──────────────────────────────────────────────────────────────
# 출력 헬퍼
# ──────────────────────────────────────────────────────────────

RESET = "\033[0m";  BOLD  = "\033[1m"
RED   = "\033[91m"; GREEN = "\033[92m"
YELLOW= "\033[93m"; CYAN  = "\033[96m"
DIM   = "\033[2m"

def _tty() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

def c(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if _tty() else text

def section_header(title: str) -> None:
    bar = "─" * 64
    print(f"\n{c(bar, CYAN)}")
    print(c(f"  {title}", BOLD + CYAN))
    print(c(bar, CYAN))

def ok(msg: str)   -> None: print(c(f"  ✓  {msg}", GREEN))
def warn(msg: str) -> None: print(c(f"  △  {msg}", YELLOW))
def fail(msg: str) -> None: print(c(f"  ✗  {msg}", RED))
def info(msg: str) -> None: print(c(f"     {msg}", DIM))


# ──────────────────────────────────────────────────────────────
# DB 스키마 조회
# ──────────────────────────────────────────────────────────────

def db_tables(cur) -> set[str]:
    cur.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'market_mvp'
          AND TABLE_TYPE   = 'BASE TABLE'
    """)
    return {r[0] for r in cur.fetchall()}


def db_pk_columns(cur) -> dict[str, str]:
    """테이블명 → PK 컬럼명 (복합 PK는 첫 번째 컬럼)"""
    cur.execute("""
        SELECT TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA    = 'market_mvp'
          AND CONSTRAINT_NAME = 'PRIMARY'
          AND ORDINAL_POSITION = 1
    """)
    return {r[0]: r[1] for r in cur.fetchall()}


def db_fk_constraints(cur) -> dict[str, list[tuple[str, str, str]]]:
    """테이블명 → [(col, ref_table, ref_col), ...]"""
    cur.execute("""
        SELECT TABLE_NAME, COLUMN_NAME,
               REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA          = 'market_mvp'
          AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY TABLE_NAME, COLUMN_NAME
    """)
    result: dict[str, list] = {}
    for tbl, col, ref_tbl, ref_col in cur.fetchall():
        result.setdefault(tbl, []).append((col, ref_tbl, ref_col))
    return result


def db_enum_columns(cur) -> dict[str, dict[str, set[str]]]:
    """테이블명 → {컬럼명: {허용값, ...}}"""
    cur.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'market_mvp'
          AND DATA_TYPE    = 'enum'
    """)
    result: dict[str, dict] = {}
    for tbl, col, col_type in cur.fetchall():
        vals = set(re.findall(r"'([^']+)'", col_type))
        result.setdefault(tbl, {})[col] = vals
    return result


def db_all_columns(cur) -> dict[str, set[str]]:
    """테이블명 → {컬럼명, ...}"""
    cur.execute("""
        SELECT TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'market_mvp'
    """)
    result: dict[str, set] = {}
    for tbl, col in cur.fetchall():
        result.setdefault(tbl, set()).add(col)
    return result


# ──────────────────────────────────────────────────────────────
# Markdown 파싱
# ──────────────────────────────────────────────────────────────

def _extract_section(text: str, prefix: str) -> str:
    """'## N.' 으로 시작하는 섹션 추출 (다음 '## ' 섹션 직전까지)"""
    pattern = rf"(?ms)(^{re.escape(prefix)}.*?)(?=^##\s|\Z)"
    m = re.search(pattern, text)
    return m.group(1) if m else ""


def parse_section3(text: str) -> list[str]:
    """섹션 3 마크다운 테이블에서 테이블명(2번째 열) 추출"""
    section = _extract_section(text, "## 3.")
    tables: list[str] = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[1].strip()
        # 헤더 행, 구분자 행 제외
        if not name or re.fullmatch(r"[:\-\s]+", name) or name == "테이블명":
            continue
        tables.append(name)
    return tables


# Section 5 파싱용 정규식
_RE_PK   = re.compile(r"\*\*PK\*\*:\s+`(\w+)")
_RE_FK   = re.compile(r"`(\w+)\s*→\s*(\w+)\.(\w+)`")
_RE_ENUM = re.compile(r"\*\*ENUM\*\*:\s+`(\w+)`\s*[—–-]+\s+(.+)")
_RE_ENUM_VAL = re.compile(r"`([^`]+)`")
# 주요 필드 / 스냅샷 필드 — 첫 번째 식별자만 (괄호·설명 전까지)
_RE_KEY_FIELDS = re.compile(
    r"\*\*(?:주요\s*필드|스냅샷\s*필드|주요필드)\*\*:\s+(.+)"
)
_RE_COL_NAME = re.compile(r"`(\w+)")


def parse_section5(text: str) -> dict[str, dict]:
    """
    섹션 5에서 테이블별 메타데이터 추출.

    반환 구조:
    {
      "TableName": {
        "pk":   [col_name, ...],
        "fk":   [(col, ref_table, ref_col), ...],
        "enum": {col: {val, ...}, ...},
        "cols": [col_name, ...],   # 주요 필드·스냅샷 필드
      },
      ...
    }
    """
    section = _extract_section(text, "## 5.")
    result: dict[str, dict] = {}
    cur_tbl: str | None = None

    for line in section.splitlines():
        # ### TableName
        m = re.match(r"^###\s+(\S+)", line)
        if m:
            cur_tbl = m.group(1)
            result[cur_tbl] = {"pk": [], "fk": [], "enum": {}, "cols": []}
            continue
        if cur_tbl is None:
            continue

        entry = result[cur_tbl]

        # PK
        m = _RE_PK.search(line)
        if m and "**PK**" in line:
            entry["pk"].append(m.group(1))
            continue

        # FK — 한 줄에 여러 개 가능: `col → Table.col`, `col2 → Table2.col2`
        if "**FK**" in line:
            for fk_m in _RE_FK.finditer(line):
                entry["fk"].append((fk_m.group(1), fk_m.group(2), fk_m.group(3)))
            continue

        # ENUM
        m = _RE_ENUM.search(line)
        if m:
            col  = m.group(1)
            vals = set(_RE_ENUM_VAL.findall(m.group(2)))
            entry["enum"][col] = vals
            continue

        # 주요 필드 / 스냅샷 필드
        m = _RE_KEY_FIELDS.search(line)
        if m:
            cols = _RE_COL_NAME.findall(m.group(1))
            entry["cols"].extend(cols)

    return result


# ──────────────────────────────────────────────────────────────
# 검증 함수
# ──────────────────────────────────────────────────────────────

class Checker:
    def __init__(self) -> None:
        self.issues: list[str] = []
        self.checks: int = 0

    def record(self, passed: bool, passed_msg: str, failed_msg: str) -> None:
        self.checks += 1
        if passed:
            ok(passed_msg)
        else:
            fail(failed_msg)
            self.issues.append(failed_msg)


def check_c1_tables(
    doc_tables: list[str],
    db_tbls: set[str],
    chk: Checker,
) -> None:
    section_header("C1. 테이블 목록 일치 여부 (섹션 3 ↔ DB)")

    doc_set = set(doc_tables)

    only_doc = doc_set - db_tbls
    only_db  = db_tbls - doc_set
    common   = doc_set & db_tbls

    chk.record(
        len(common) == len(doc_set) == len(db_tbls),
        f"테이블 {len(common)}개 모두 일치",
        f"불일치 존재 — 공통 {len(common)}개 / 문서만 {len(only_doc)}개 / DB만 {len(only_db)}개",
    )
    for t in sorted(only_doc):
        info(f"문서에만 존재 (DB에 없음): {t}")
    for t in sorted(only_db):
        info(f"DB에만 존재 (문서에 없음): {t}")


def check_c2_pk(
    doc_sec5: dict[str, dict],
    db_pks: dict[str, str],
    db_tbls: set[str],
    chk: Checker,
) -> None:
    section_header("C2. PK 컬럼 일치 여부 (섹션 5 ↔ DB PRIMARY KEY)")

    for tbl, meta in doc_sec5.items():
        if tbl not in db_tbls:
            warn(f"{tbl}: DB에 테이블 없음 — PK 검증 생략")
            continue
        if not meta["pk"]:
            warn(f"{tbl}: 문서에 PK 정의 없음")
            continue

        doc_pk = meta["pk"][0]
        db_pk  = db_pks.get(tbl, "")
        chk.record(
            doc_pk == db_pk,
            f"{tbl}.{doc_pk}: PK 일치",
            f"{tbl}: PK 불일치 — 문서=`{doc_pk}` / DB=`{db_pk}`",
        )


def check_c3_fk(
    doc_sec5: dict[str, dict],
    db_fks: dict[str, list],
    db_tbls: set[str],
    chk: Checker,
) -> None:
    section_header("C3. FK 관계 일치 여부 (섹션 5 ↔ DB FOREIGN KEY)")

    for tbl, meta in doc_sec5.items():
        if not meta["fk"]:
            continue
        if tbl not in db_tbls:
            warn(f"{tbl}: DB에 테이블 없음 — FK 검증 생략")
            continue

        db_fk_set = {
            (col, ref_tbl, ref_col)
            for col, ref_tbl, ref_col in db_fks.get(tbl, [])
        }

        for col, ref_tbl, ref_col in meta["fk"]:
            chk.record(
                (col, ref_tbl, ref_col) in db_fk_set,
                f"{tbl}.{col} → {ref_tbl}.{ref_col}: FK 일치",
                f"{tbl}.{col} → {ref_tbl}.{ref_col}: FK 없음 (DB에 미정의)",
            )


def check_c4_enum(
    doc_sec5: dict[str, dict],
    db_enums: dict[str, dict],
    db_tbls: set[str],
    chk: Checker,
) -> None:
    section_header("C4. ENUM 값 일치 여부 (섹션 5 ↔ DB COLUMN_TYPE)")

    for tbl, meta in doc_sec5.items():
        if not meta["enum"]:
            continue
        if tbl not in db_tbls:
            warn(f"{tbl}: DB에 테이블 없음 — ENUM 검증 생략")
            continue

        tbl_db_enums = db_enums.get(tbl, {})

        for col, doc_vals in meta["enum"].items():
            if col not in tbl_db_enums:
                chk.record(
                    False,
                    "",
                    f"{tbl}.{col}: DB에 ENUM 컬럼 없음",
                )
                continue

            db_vals  = tbl_db_enums[col]
            only_doc = doc_vals - db_vals
            only_db  = db_vals - doc_vals

            chk.record(
                not only_doc and not only_db,
                f"{tbl}.{col}: ENUM 값 일치 {sorted(doc_vals)}",
                f"{tbl}.{col}: ENUM 불일치 — "
                f"문서만={sorted(only_doc)} / DB만={sorted(only_db)}",
            )


def check_c5_columns(
    doc_sec5: dict[str, dict],
    db_cols: dict[str, set],
    db_tbls: set[str],
    chk: Checker,
) -> None:
    section_header("C5. 주요 컬럼 존재 여부 (섹션 5 ↔ DB 컬럼 목록)")

    for tbl, meta in doc_sec5.items():
        if tbl not in db_tbls:
            continue

        tbl_db_cols = db_cols.get(tbl, set())
        # PK·FK 컬럼도 함께 확인
        all_doc_cols = (
            meta["pk"]
            + [col for col, _, _ in meta["fk"]]
            + list(meta["enum"].keys())
            + meta["cols"]
        )

        seen: set[str] = set()
        for col in all_doc_cols:
            if col in seen:
                continue
            seen.add(col)
            chk.record(
                col in tbl_db_cols,
                f"{tbl}.{col}: 컬럼 존재",
                f"{tbl}.{col}: DB에 컬럼 없음",
            )


# ──────────────────────────────────────────────────────────────
# 결과 요약
# ──────────────────────────────────────────────────────────────

def print_summary(chk: Checker) -> None:
    bar = "─" * 64
    passed = chk.checks - len(chk.issues)
    print(f"\n{c(bar, CYAN)}")
    print(c("  검증 결과 요약", BOLD + CYAN))
    print(c(bar, CYAN))
    print(f"  전체 검사 항목  : {c(str(chk.checks), BOLD)}개")
    print(f"  {c('통과', GREEN)}           : {c(str(passed), GREEN)}개")
    print(f"  {c('불일치', RED)}         : {c(str(len(chk.issues)), RED)}개")

    if chk.issues:
        print(c(f"\n  불일치 항목 ({len(chk.issues)}건):", BOLD + RED))
        for i, issue in enumerate(chk.issues, 1):
            print(c(f"  {i:>2}. {issue}", RED))
    else:
        print(c("\n  문서와 DB 스키마가 완전히 일치합니다.", GREEN + BOLD))

    print(c(bar, CYAN) + "\n")


# ──────────────────────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────────────────────

def main() -> None:
    # ── 보고서 로드 ──────────────────────────────────────────
    if not REPORT_PATH.exists():
        sys.exit(f"[ERROR] 보고서 파일을 찾을 수 없습니다: {REPORT_PATH}")

    md_text = REPORT_PATH.read_text(encoding="utf-8")

    print(c("\n▶  db_setup_report.md ↔ MySQL 스키마 불일치 검증", BOLD))
    print(c(f"   보고서: {REPORT_PATH}", DIM))
    print(c(f"   DB    : {DB_CONFIG['host']}:{DB_CONFIG['port']}"
            f"  database={DB_CONFIG['database']}", DIM))

    # ── Markdown 파싱 ────────────────────────────────────────
    doc_tables = parse_section3(md_text)
    doc_sec5   = parse_section5(md_text)

    if not doc_tables:
        sys.exit("[ERROR] 섹션 3을 파싱할 수 없습니다. 마크다운 형식을 확인하세요.")
    if not doc_sec5:
        sys.exit("[ERROR] 섹션 5를 파싱할 수 없습니다. 마크다운 형식을 확인하세요.")

    print(c(f"\n   섹션 3 파싱: 테이블 {len(doc_tables)}개", DIM))
    print(c(f"   섹션 5 파싱: 테이블 정의 {len(doc_sec5)}개", DIM))

    # ── DB 연결 ──────────────────────────────────────────────
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        sys.exit(f"\n[ERROR] DB 연결 실패: {e}\n"
                 "  .env 파일의 DB_USER / DB_PASSWORD / DB_HOST 를 확인하세요.")

    cur = conn.cursor()

    try:
        db_tbls  = db_tables(cur)
        db_pks   = db_pk_columns(cur)
        db_fks   = db_fk_constraints(cur)
        db_enums = db_enum_columns(cur)
        db_cols  = db_all_columns(cur)
    except mysql.connector.Error as e:
        conn.close()
        sys.exit(f"[ERROR] INFORMATION_SCHEMA 조회 실패: {e}")

    # ── 검증 실행 ────────────────────────────────────────────
    chk = Checker()
    check_c1_tables(doc_tables, db_tbls, chk)
    check_c2_pk(doc_sec5, db_pks, db_tbls, chk)
    check_c3_fk(doc_sec5, db_fks, db_tbls, chk)
    check_c4_enum(doc_sec5, db_enums, db_tbls, chk)
    check_c5_columns(doc_sec5, db_cols, db_tbls, chk)

    cur.close()
    conn.close()

    print_summary(chk)
    sys.exit(1 if chk.issues else 0)


if __name__ == "__main__":
    main()
