"""
verify.py — market_mvp 데이터베이스 검증 스크립트

조회 항목:
  1. 전체 테이블별 row 수
  2. Market별 Store 수
  3. Store별 Product 수와 평균 가격
  4. 오늘 예정된 DropEvent 목록
  5. User별 ShoppingList와 아이템 수
  6. 미읽음 Notification 수 (사용자별)
  7. RoutePlan 경유 점포 수 평균
"""

import os
import sys
from pathlib import Path
from datetime import date

# .env 로드 (python-dotenv 없이)
def _load_dotenv():
    for candidate in [Path(".env"), Path(__file__).parent.parent / ".env"]:
        if candidate.exists():
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
    sys.exit("[ERROR] mysql-connector-python이 설치되지 않았습니다.\n"
             "  pip install mysql-connector-python")

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "127.0.0.1"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": "market_mvp",
}

# ──────────────────────────────────────────────
# 출력 헬퍼
# ──────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
DIM    = "\033[2m"

def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

def c(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if _supports_color() else text

def header(title: str) -> None:
    width = 62
    bar = "─" * width
    print(f"\n{c(bar, CYAN)}")
    print(c(f"  {title}", BOLD + CYAN))
    print(c(bar, CYAN))

def table(columns: list[str], rows: list[tuple], col_widths: list[int] | None = None) -> None:
    if not rows:
        print(c("  (데이터 없음)", DIM))
        return

    # 자동 너비 계산
    widths = [len(col) for col in columns]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    if col_widths:
        widths = [max(a, b) for a, b in zip(widths, col_widths)]

    sep = "  " + "  ".join("─" * w for w in widths)
    header_row = "  " + "  ".join(
        c(col.ljust(widths[i]), BOLD) for i, col in enumerate(columns)
    )

    print(sep)
    print(header_row)
    print(sep)
    for i, row in enumerate(rows):
        color = "" if i % 2 == 0 else DIM
        cells = "  ".join(str(cell).ljust(widths[j]) for j, cell in enumerate(row))
        print(c("  " + cells, color))
    print(sep)

def summary(label: str, value) -> None:
    print(f"  {c(label, BOLD)}: {c(str(value), GREEN)}")


# ──────────────────────────────────────────────
# 검증 쿼리
# ──────────────────────────────────────────────

TABLES = [
    "Market", "User", "Store", "Merchant", "Product",
    "DropEvent", "CatalogItem", "ShoppingList", "ShoppingListItem",
    "RoutePlan", "Notification", "Preorder",
]


def check_table_counts(cur) -> None:
    header("1. 전체 테이블별 row 수")
    rows = []
    total = 0
    for tbl in TABLES:
        cur.execute(f"SELECT COUNT(*) FROM `{tbl}`")
        cnt = cur.fetchone()[0]
        total += cnt
        rows.append((tbl, f"{cnt:,}"))
    table(["테이블", "rows"], rows, [20, 8])
    summary("전체 합계", f"{total:,}개")


def check_market_stores(cur) -> None:
    header("2. Market별 Store 수")
    cur.execute("""
        SELECT m.market_name,
               COUNT(s.store_id)  AS store_cnt,
               GROUP_CONCAT(s.zone_label ORDER BY s.zone_label SEPARATOR ' / ') AS zones
        FROM Market m
        LEFT JOIN Store s ON s.market_id = m.market_id
        GROUP BY m.market_id, m.market_name
        ORDER BY store_cnt DESC
    """)
    rows = [(r[0], r[1], r[2] or "-") for r in cur.fetchall()]
    table(["시장명", "점포 수", "구역 목록"], rows, [12, 6, 30])


def check_store_products(cur) -> None:
    header("3. Store별 Product 수 / 평균 가격")
    cur.execute("""
        SELECT s.store_name,
               s.zone_label,
               COUNT(p.product_id)               AS cnt,
               FORMAT(AVG(p.price), 0)            AS avg_price,
               SUM(p.stock_status = 'in_stock')   AS in_s,
               SUM(p.stock_status = 'low_stock')  AS low_s,
               SUM(p.stock_status = 'out_of_stock') AS out_s
        FROM Store s
        LEFT JOIN Product p ON p.store_id = s.store_id
        GROUP BY s.store_id, s.store_name, s.zone_label
        ORDER BY s.zone_label, s.store_name
    """)
    rows = [
        (r[0], r[1], r[2],
         f"{r[3]}원" if r[3] else "-",
         f"✓{r[4]} △{r[5]} ✗{r[6]}")
        for r in cur.fetchall()
    ]
    table(["점포명", "구역", "상품수", "평균가격", "재고(정상/부족/품절)"],
          rows, [14, 6, 5, 10, 16])


def check_today_drops(cur) -> None:
    header("4. 오늘 예정된 DropEvent 목록")
    today = date.today().isoformat()
    cur.execute("""
        SELECT d.expected_at,
               s.store_name,
               p.product_name,
               FORMAT(p.price, 0)  AS price,
               d.status
        FROM DropEvent d
        JOIN Store   s ON s.store_id   = d.store_id
        JOIN Product p ON p.product_id = d.product_id
        WHERE DATE(d.expected_at) = %s
        ORDER BY d.expected_at
    """, (today,))
    rows = cur.fetchall()
    if rows:
        rows = [(str(r[0])[11:16], r[1], r[2], f"{r[3]}원", r[4]) for r in rows]
    table(["예정시각", "점포", "상품명", "가격", "상태"],
          rows, [6, 12, 20, 10, 10])
    summary("조회 기준일", today)


def check_user_shoppinglists(cur) -> None:
    header("5. User별 ShoppingList와 아이템 수")
    cur.execute("""
        SELECT u.name,
               u.role,
               sl.title,
               COUNT(sli.list_item_id)             AS total_items,
               SUM(sli.checked)                    AS checked_cnt,
               COUNT(sli.list_item_id)
                 - COALESCE(SUM(sli.checked), 0)   AS remaining
        FROM User u
        JOIN ShoppingList sl
          ON sl.user_id = u.user_id
        LEFT JOIN ShoppingListItem sli
          ON sli.shopping_list_id = sl.shopping_list_id
        GROUP BY u.user_id, u.name, u.role, sl.shopping_list_id, sl.title
        ORDER BY u.name, sl.title
    """)
    rows = [(r[0], r[1], r[2], r[3], f"{r[4]}개 완료", f"{r[5]}개 남음")
            for r in cur.fetchall()]
    table(["이름", "역할", "목록 제목", "전체", "완료", "잔여"],
          rows, [8, 10, 16, 4, 8, 8])


def check_unread_notifications(cur) -> None:
    header("6. 미읽음 Notification 수")
    cur.execute("""
        SELECT u.name,
               u.role,
               COUNT(*)                                          AS total_ntf,
               SUM(n.is_read = 0)                               AS unread,
               GROUP_CONCAT(DISTINCT n.type ORDER BY n.type
                            SEPARATOR ', ')                      AS types
        FROM User u
        JOIN Notification n ON n.user_id = u.user_id
        GROUP BY u.user_id, u.name, u.role
        ORDER BY unread DESC
    """)
    rows = [(r[0], r[1], r[2], c(str(r[3]), YELLOW) if r[3] else "0", r[4])
            for r in cur.fetchall()]
    table(["이름", "역할", "전체 알림", "미읽음", "알림 유형"], rows, [8, 10, 8, 6, 30])

    cur.execute("SELECT COUNT(*) FROM Notification WHERE is_read = 0")
    summary("전체 미읽음 합계", f"{cur.fetchone()[0]}개")


def check_route_plan_stats(cur) -> None:
    header("7. RoutePlan 경유 점포 수 평균")
    cur.execute("""
        SELECT u.name,
               m.market_name,
               JSON_LENGTH(rp.route_json, '$.steps')           AS step_cnt,
               JSON_UNQUOTE(
                 JSON_EXTRACT(rp.route_json, '$.total_distance_m')
               )                                               AS dist_m,
               JSON_UNQUOTE(
                 JSON_EXTRACT(rp.route_json, '$.estimated_time_min')
               )                                               AS time_min
        FROM RoutePlan rp
        JOIN User   u ON u.user_id   = rp.user_id
        JOIN Market m ON m.market_id = rp.market_id
        ORDER BY u.name
    """)
    raw = cur.fetchall()
    rows = [(r[0], r[1], f"{r[2]}개 점포", f"{r[3]}m", f"{r[4]}분")
            for r in raw]
    table(["사용자", "시장", "경유 점포", "총 거리", "예상 시간"],
          rows, [8, 10, 8, 8, 8])

    if raw:
        avg_steps = sum(r[2] for r in raw) / len(raw)
        avg_dist  = sum(int(r[3]) for r in raw) / len(raw)
        avg_time  = sum(int(r[4]) for r in raw) / len(raw)
        summary("경유 점포 평균", f"{avg_steps:.1f}개")
        summary("총 거리 평균",   f"{avg_dist:.0f}m")
        summary("소요 시간 평균", f"{avg_time:.0f}분")


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────

CHECKS = [
    check_table_counts,
    check_market_stores,
    check_store_products,
    check_today_drops,
    check_user_shoppinglists,
    check_unread_notifications,
    check_route_plan_stats,
]


def main() -> None:
    print(c("\n▶  market_mvp DB 검증 시작", BOLD))
    print(c(f"   host={DB_CONFIG['host']}  db={DB_CONFIG['database']}", DIM))

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        sys.exit(f"\n[ERROR] DB 연결 실패: {e}\n"
                 "  .env 파일의 DB_USER / DB_PASSWORD / DB_HOST 를 확인하세요.")

    cur = conn.cursor()
    errors: list[str] = []

    for fn in CHECKS:
        try:
            fn(cur)
        except mysql.connector.Error as e:
            print(c(f"  [SKIP] {fn.__name__}: {e}", YELLOW))
            errors.append(fn.__name__)

    cur.close()
    conn.close()

    print(c("\n▶  검증 완료", BOLD))
    if errors:
        print(c(f"   실패 항목: {', '.join(errors)}", YELLOW))
    else:
        print(c("   모든 항목 정상", GREEN))
    print()


if __name__ == "__main__":
    main()
