"""
init_db.py — 1회성 수동 실행 스크립트
Railway DB에 스키마가 이미 존재하는 경우에는 실행 불필요.
schema.sql 적용 후 서버 코드와 __tablename__ 불일치가 발생할 때 사용.

실행 방법:
  cd server
  python -m scripts.init_db
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import engine, Base

import app.db.models.user          # noqa: F401
import app.db.models.market        # noqa: F401
import app.db.models.store         # noqa: F401
import app.db.models.merchant      # noqa: F401
import app.db.models.product       # noqa: F401
import app.db.models.drop_event    # noqa: F401
import app.db.models.catalog_item  # noqa: F401
import app.db.models.shopping_list # noqa: F401
import app.db.models.shopping_list_item  # noqa: F401
import app.db.models.route_plan    # noqa: F401
import app.db.models.notification  # noqa: F401


def main():
    print("Creating tables (checkfirst=True — 기존 테이블 유지)...")
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Done.")


if __name__ == "__main__":
    main()
