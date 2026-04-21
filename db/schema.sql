-- =============================================================
-- 전통시장 서비스 MVP Database Schema
-- Environment : macOS Homebrew, MySQL 8.0
-- Encoding    : utf8mb4 / utf8mb4_unicode_ci
-- Engine      : InnoDB
-- Created     : 2026-04-18
-- =============================================================

CREATE DATABASE IF NOT EXISTS market_mvp
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE market_mvp;

-- =============================================================
-- 1. Market
--    전통시장 기본 정보 (위치, 이름)
-- =============================================================
CREATE TABLE IF NOT EXISTS Market (
  market_id   VARCHAR(36)    NOT NULL,
  market_name VARCHAR(100)   NOT NULL,
  address     VARCHAR(255)   NOT NULL,
  lat         DECIMAL(10,7)  NOT NULL,
  lng         DECIMAL(10,7)  NOT NULL,
  created_at  DATETIME       DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (market_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 2. User
--    서비스 사용자 (소비자 / 상인 / 운영자)
-- =============================================================
CREATE TABLE IF NOT EXISTS User (
  user_id    VARCHAR(36)                              NOT NULL,
  email      VARCHAR(255)                             NOT NULL,
  password   VARCHAR(255)                             NOT NULL,
  role       ENUM('consumer','merchant','operator')   NOT NULL,
  name       VARCHAR(100)                             NOT NULL,
  phone      VARCHAR(20)                              NULL,
  home_market_id VARCHAR(36)                          NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 3. Store
--    시장 내 개별 점포
-- =============================================================
CREATE TABLE IF NOT EXISTS Store (
  store_id   VARCHAR(36)  NOT NULL,
  market_id  VARCHAR(36)  NOT NULL,
  store_name VARCHAR(100) NOT NULL,
  zone_label VARCHAR(50)  NOT NULL,
  lat        DECIMAL(10,7) NULL,
  lng        DECIMAL(10,7) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (store_id),
  CONSTRAINT fk_store_market FOREIGN KEY (market_id)
    REFERENCES Market (market_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 4. Merchant
--    점포를 운영하는 상인 (User와 Store를 연결)
-- =============================================================
CREATE TABLE IF NOT EXISTS Merchant (
  merchant_id  VARCHAR(36)  NOT NULL,
  store_id     VARCHAR(36)  NOT NULL,
  user_id      VARCHAR(36)  NOT NULL,
  display_name VARCHAR(100) NOT NULL,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (merchant_id),
  CONSTRAINT fk_merchant_store FOREIGN KEY (store_id)
    REFERENCES Store (store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_merchant_user FOREIGN KEY (user_id)
    REFERENCES User (user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 5. Product
--    점포에서 판매하는 상품
-- =============================================================
CREATE TABLE IF NOT EXISTS Product (
  product_id   VARCHAR(36)  NOT NULL,
  store_id     VARCHAR(36)  NOT NULL,
  product_name VARCHAR(100) NOT NULL,
  price        INT          NOT NULL,
  stock_status ENUM('in_stock','low_stock','out_of_stock') NOT NULL DEFAULT 'in_stock',
  image_url    VARCHAR(500) NULL,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (product_id),
  CONSTRAINT fk_product_store FOREIGN KEY (store_id)
    REFERENCES Store (store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 6. DropEvent
--    입고 예정 / 한정 판매 이벤트
-- =============================================================
CREATE TABLE IF NOT EXISTS DropEvent (
  drop_id     VARCHAR(36) NOT NULL,
  product_id  VARCHAR(36) NOT NULL,
  store_id    VARCHAR(36) NOT NULL,
  expected_at DATETIME    NOT NULL,
  status      ENUM('scheduled','arrived','sold_out') NOT NULL DEFAULT 'scheduled',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (drop_id),
  CONSTRAINT fk_drop_product FOREIGN KEY (product_id)
    REFERENCES Product (product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_drop_store FOREIGN KEY (store_id)
    REFERENCES Store (store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 7. CatalogItem
--    시장 단위 카탈로그 (드랍/상품/이벤트 스냅샷)
-- =============================================================
CREATE TABLE IF NOT EXISTS CatalogItem (
  catalog_item_id  VARCHAR(36)  NOT NULL,
  market_id        VARCHAR(36)  NOT NULL,
  item_type        ENUM('drop','product','event') NOT NULL,
  title            VARCHAR(200) NOT NULL,
  title_snapshot   VARCHAR(200) NOT NULL,
  image_snapshot   VARCHAR(500) NULL,
  price_snapshot   INT          NULL,
  created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (catalog_item_id),
  CONSTRAINT fk_catalog_market FOREIGN KEY (market_id)
    REFERENCES Market (market_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 8. ShoppingList
--    사용자 장보기 목록
-- =============================================================
CREATE TABLE IF NOT EXISTS ShoppingList (
  shopping_list_id VARCHAR(36)  NOT NULL,
  user_id          VARCHAR(36)  NOT NULL,
  title            VARCHAR(200) NOT NULL,
  created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (shopping_list_id),
  CONSTRAINT fk_shoppinglist_user FOREIGN KEY (user_id)
    REFERENCES User (user_id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 9. ShoppingListItem
--    장보기 목록 내 개별 항목
-- =============================================================
CREATE TABLE IF NOT EXISTS ShoppingListItem (
  list_item_id          VARCHAR(36)  NOT NULL,
  shopping_list_id      VARCHAR(36)  NOT NULL,
  product_name_snapshot VARCHAR(200) NOT NULL,
  qty                   INT          NOT NULL,
  unit                  VARCHAR(20)  NOT NULL,
  checked               TINYINT(1)   NOT NULL DEFAULT 0,
  created_at            DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (list_item_id),
  CONSTRAINT fk_listitem_shoppinglist FOREIGN KEY (shopping_list_id)
    REFERENCES ShoppingList (shopping_list_id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 10. RoutePlan
--     사용자별 시장 동선 계획 (JSON으로 경로 저장)
-- =============================================================
CREATE TABLE IF NOT EXISTS RoutePlan (
  route_plan_id VARCHAR(36) NOT NULL,
  user_id       VARCHAR(36) NOT NULL,
  market_id     VARCHAR(36) NOT NULL,
  route_json    JSON        NOT NULL,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (route_plan_id),
  CONSTRAINT fk_routeplan_user FOREIGN KEY (user_id)
    REFERENCES User (user_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_routeplan_market FOREIGN KEY (market_id)
    REFERENCES Market (market_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 11. Notification
--     사용자 알림 (드랍, 입고, 이벤트 등)
-- =============================================================
CREATE TABLE IF NOT EXISTS Notification (
  notification_id VARCHAR(36)  NOT NULL,
  user_id         VARCHAR(36)  NOT NULL,
  type            VARCHAR(50)  NOT NULL,
  title           VARCHAR(200) NOT NULL,
  target_type     VARCHAR(50)  NOT NULL,
  target_id       VARCHAR(36)  NOT NULL,
  is_read         TINYINT(1)   NOT NULL DEFAULT 0,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (notification_id),
  CONSTRAINT fk_notification_user FOREIGN KEY (user_id)
    REFERENCES User (user_id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- 12. Preorder
--     사전 주문 / 예약 구매 요청
-- =============================================================
CREATE TABLE IF NOT EXISTS Preorder (
  preorder_id  VARCHAR(36)  NOT NULL,
  user_id      VARCHAR(36)  NOT NULL,
  store_id     VARCHAR(36)  NOT NULL,
  product_name VARCHAR(100) NOT NULL,
  qty          INT          NOT NULL,
  status       ENUM('requested','confirmed','ready','cancelled') NOT NULL DEFAULT 'requested',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (preorder_id),
  CONSTRAINT fk_preorder_user FOREIGN KEY (user_id)
    REFERENCES User (user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_preorder_store FOREIGN KEY (store_id)
    REFERENCES Store (store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- FK 관계도 요약
-- =============================================================
--
--  Market (1) ──────────────< (N) Store
--  Market (1) ──────────────< (N) CatalogItem
--  Market (1) ──────────────< (N) RoutePlan
--
--  User   (1) ──────────────< (N) Merchant
--  User   (1) ──────────────< (N) ShoppingList
--  User   (1) ──────────────< (N) RoutePlan
--  User   (1) ──────────────< (N) Notification
--  User   (1) ──────────────< (N) Preorder
--
--  Store  (1) ──────────────< (N) Merchant
--  Store  (1) ──────────────< (N) Product
--  Store  (1) ──────────────< (N) DropEvent
--  Store  (1) ──────────────< (N) Preorder
--
--  Product      (1) ────────< (N) DropEvent
--  ShoppingList (1) ────────< (N) ShoppingListItem
--
--  전체 요약:
--
--  Market (1) ──< (N) Store  (1) ──< (N) Product   (1) ──< (N) DropEvent
--                     │
--                     └──────────────< (N) Merchant ──> (1) User
--                     └──────────────< (N) Preorder ──> (1) User
--
--  Market (1) ──< (N) CatalogItem
--  Market (1) ──< (N) RoutePlan   ──> (1) User
--
--  User   (1) ──< (N) ShoppingList (1) ──< (N) ShoppingListItem
--  User   (1) ──< (N) Notification
--
-- =============================================================
