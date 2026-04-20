-- =============================================================
-- MarketPrice 테이블 추가
-- KAMIS 농산물 시세 기준 가격 저장 (상인 판매가 비교 근거)
-- =============================================================

USE market_mvp;

CREATE TABLE IF NOT EXISTS MarketPrice (
  market_price_id  VARCHAR(36)   NOT NULL,
  item_name        VARCHAR(100)  NOT NULL COMMENT 'KAMIS 품목명 (예: 배추/포기)',
  kamis_item_code  VARCHAR(20)   NOT NULL COMMENT 'KAMIS 품목 코드',
  unit             VARCHAR(50)   NOT NULL COMMENT '단위 (예: 1포기, 1kg)',
  price_date       DATE          NOT NULL COMMENT '가격 기준일',
  retail_price     INT           NULL     COMMENT '당일 소매가 (dpr1)',
  prev_day_price   INT           NULL     COMMENT '전일 가격 (dpr2)',
  prev_month_price INT           NULL     COMMENT '전월 가격 (dpr3)',
  prev_year_price  INT           NULL     COMMENT '전년 가격 (dpr4)',
  created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (market_price_id),
  UNIQUE KEY uq_item_date (kamis_item_code, item_name, price_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='KAMIS 농산물유통정보 시세 기준 가격 (상인 판매가 비교용)';
