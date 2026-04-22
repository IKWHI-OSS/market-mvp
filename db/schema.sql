-- =============================================================================
-- Market MVP — Database Schema
-- Synced from Railway MySQL 8.0 on 2026-04-22
-- Character set: utf8mb4 / Collation: utf8mb4_unicode_ci
--
-- Table order respects FK dependency graph (parent → child).
-- Apply with: mysql -h <host> -u <user> -p market_mvp < schema.sql
--
-- NOTE: Legacy lowercase tables (market, store, product, ...) also exist in
-- Railway DB from an earlier migration. They are NOT part of the application
-- schema and will be removed in a future cleanup migration.
-- =============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------------------------
-- Market  (no FK deps)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Market` (
  `market_id`   VARCHAR(36)    NOT NULL,
  `market_name` VARCHAR(100)   NOT NULL,
  `address`     VARCHAR(255)   NOT NULL,
  `lat`         DECIMAL(10,7)  NOT NULL,
  `lng`         DECIMAL(10,7)  NOT NULL,
  `created_at`  DATETIME       DEFAULT CURRENT_TIMESTAMP,
  `region_code` VARCHAR(20)    DEFAULT NULL,
  `zoom`        DECIMAL(5,2)   NOT NULL DEFAULT '15.00',
  `market_desc` TEXT           DEFAULT NULL,
  `open_hours`  VARCHAR(255)   DEFAULT NULL,
  PRIMARY KEY (`market_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- MarketPrice  (no FK deps — KAMIS 시세 참조 테이블)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `MarketPrice` (
  `market_price_id`  VARCHAR(36)  NOT NULL,
  `item_name`        VARCHAR(100) NOT NULL COMMENT 'KAMIS 품목명 (예: 배추/포기)',
  `kamis_item_code`  VARCHAR(20)  NOT NULL COMMENT 'KAMIS 품목 코드',
  `unit`             VARCHAR(50)  NOT NULL COMMENT '단위 (예: 1포기, 1kg)',
  `price_date`       DATE         NOT NULL COMMENT '가격 기준일',
  `retail_price`     INT          DEFAULT NULL COMMENT '당일 소매가 (dpr1)',
  `prev_day_price`   INT          DEFAULT NULL COMMENT '전일 가격 (dpr2)',
  `prev_month_price` INT          DEFAULT NULL COMMENT '전월 가격 (dpr3)',
  `prev_year_price`  INT          DEFAULT NULL COMMENT '전년 가격 (dpr4)',
  `created_at`       DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`market_price_id`),
  UNIQUE KEY `uq_item_date` (`kamis_item_code`, `item_name`, `price_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='KAMIS 농산물유통정보 시세 기준 가격 (상인 판매가 비교용)';

-- -----------------------------------------------------------------------------
-- User  (no FK deps)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `User` (
  `user_id`        VARCHAR(36)  NOT NULL,
  `email`          VARCHAR(255) NOT NULL,
  `password`       VARCHAR(255) NOT NULL,
  `role`           ENUM('consumer','merchant','operator') NOT NULL,
  `name`           VARCHAR(100) NOT NULL,
  `phone`          VARCHAR(20)  DEFAULT NULL,
  `home_market_id` VARCHAR(36)  DEFAULT NULL,
  `created_at`     DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uq_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Store  (→ Market)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Store` (
  `store_id`            VARCHAR(36)   NOT NULL,
  `market_id`           VARCHAR(36)   NOT NULL,
  `store_name`          VARCHAR(100)  NOT NULL,
  `zone_label`          VARCHAR(50)   NOT NULL,
  `lat`                 DECIMAL(10,7) DEFAULT NULL,
  `lng`                 DECIMAL(10,7) DEFAULT NULL,
  `phone`               VARCHAR(20)   DEFAULT NULL,
  `status`              VARCHAR(20)   DEFAULT 'open',
  `store_story_summary` TEXT          DEFAULT NULL,
  `open_hours`          VARCHAR(255)  DEFAULT NULL,
  `updated_at`          DATETIME      DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `created_at`          DATETIME      DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`store_id`),
  KEY `fk_store_market` (`market_id`),
  CONSTRAINT `fk_store_market`
    FOREIGN KEY (`market_id`) REFERENCES `Market` (`market_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Merchant  (→ Store, User)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Merchant` (
  `merchant_id`       VARCHAR(36)  NOT NULL,
  `store_id`          VARCHAR(36)  NOT NULL,
  `user_id`           VARCHAR(36)  NOT NULL,
  `display_name`      VARCHAR(100) NOT NULL,
  `description`       TEXT         DEFAULT NULL,
  `profile_image_url` VARCHAR(500) DEFAULT NULL,
  `active`            TINYINT(1)   NOT NULL DEFAULT '1',
  `created_at`        DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`merchant_id`),
  KEY `fk_merchant_store` (`store_id`),
  KEY `fk_merchant_user`  (`user_id`),
  CONSTRAINT `fk_merchant_store`
    FOREIGN KEY (`store_id`) REFERENCES `Store` (`store_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_merchant_user`
    FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Product  (→ Store)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Product` (
  `product_id`   VARCHAR(36)  NOT NULL,
  `store_id`     VARCHAR(36)  NOT NULL,
  `product_name` VARCHAR(100) NOT NULL,
  `category`     VARCHAR(100) DEFAULT NULL,
  `price`        INT          NOT NULL,
  `stock_status` ENUM('in_stock','low_stock','out_of_stock') NOT NULL DEFAULT 'in_stock',
  `image_url`    VARCHAR(500) DEFAULT NULL,
  `quality_note` TEXT         DEFAULT NULL,
  `updated_at`   DATETIME     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `created_at`   DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`product_id`),
  KEY `fk_product_store` (`store_id`),
  CONSTRAINT `fk_product_store`
    FOREIGN KEY (`store_id`) REFERENCES `Store` (`store_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- DropEvent  (→ Product, Store)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `DropEvent` (
  `drop_id`          VARCHAR(36)  NOT NULL,
  `product_id`       VARCHAR(36)  NOT NULL,
  `store_id`         VARCHAR(36)  NOT NULL,
  `title`            VARCHAR(255) DEFAULT NULL,
  `expected_at`      DATETIME     NOT NULL,
  `status`           ENUM('scheduled','arrived','sold_out') NOT NULL DEFAULT 'scheduled',
  `subscriber_count` INT          NOT NULL DEFAULT '0',
  `updated_at`       DATETIME     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `created_at`       DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`drop_id`),
  KEY `fk_drop_product` (`product_id`),
  KEY `fk_drop_store`   (`store_id`),
  CONSTRAINT `fk_drop_product`
    FOREIGN KEY (`product_id`) REFERENCES `Product` (`product_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_drop_store`
    FOREIGN KEY (`store_id`) REFERENCES `Store` (`store_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- DropSubscription  (→ DropEvent, User)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `DropSubscription` (
  `subscription_id` VARCHAR(36) NOT NULL,
  `drop_id`         VARCHAR(36) NOT NULL,
  `user_id`         VARCHAR(36) NOT NULL,
  `created_at`      DATETIME    DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`subscription_id`),
  UNIQUE KEY `uq_drop_subscription` (`drop_id`, `user_id`),
  KEY `fk_ds_user` (`user_id`),
  CONSTRAINT `fk_ds_drop`
    FOREIGN KEY (`drop_id`) REFERENCES `DropEvent` (`drop_id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_ds_user`
    FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- CatalogItem  (→ Market)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `CatalogItem` (
  `catalog_item_id` VARCHAR(36)  NOT NULL,
  `market_id`       VARCHAR(36)  NOT NULL,
  `store_id`        VARCHAR(36)  DEFAULT NULL,
  `product_id`      VARCHAR(36)  DEFAULT NULL,
  `item_type`       ENUM('drop','event','store_spotlight') NOT NULL,
  `title`           VARCHAR(200) NOT NULL,
  `title_snapshot`  VARCHAR(200) NOT NULL,
  `image_snapshot`  VARCHAR(500) DEFAULT NULL,
  `price_snapshot`  INT          DEFAULT NULL,
  `badge`           VARCHAR(100) DEFAULT NULL,
  `start_at`        DATETIME     DEFAULT NULL,
  `end_at`          DATETIME     DEFAULT NULL,
  `priority`        INT          NOT NULL DEFAULT '0',
  `created_at`      DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`catalog_item_id`),
  KEY `fk_catalog_market` (`market_id`),
  CONSTRAINT `fk_catalog_market`
    FOREIGN KEY (`market_id`) REFERENCES `Market` (`market_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- ShoppingList  (→ User)
-- NOTE: total_estimated_price, updated_at were added via ALTER TABLE;
-- column order reflects Railway DB state.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `ShoppingList` (
  `shopping_list_id`      VARCHAR(36)  NOT NULL,
  `user_id`               VARCHAR(36)  NOT NULL,
  `title`                 VARCHAR(200) NOT NULL,
  `created_at`            DATETIME     DEFAULT CURRENT_TIMESTAMP,
  `total_estimated_price` INT          DEFAULT NULL,
  `updated_at`            DATETIME     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`shopping_list_id`),
  KEY `fk_shoppinglist_user` (`user_id`),
  CONSTRAINT `fk_shoppinglist_user`
    FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- ShoppingListItem  (→ ShoppingList)
-- NOTE: product_id, estimated_price, store_id were added via ALTER TABLE;
-- column order reflects Railway DB state.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `ShoppingListItem` (
  `list_item_id`          VARCHAR(36)  NOT NULL,
  `shopping_list_id`      VARCHAR(36)  NOT NULL,
  `product_name_snapshot` VARCHAR(200) NOT NULL,
  `qty`                   INT          NOT NULL,
  `unit`                  VARCHAR(20)  NOT NULL,
  `checked`               TINYINT(1)   NOT NULL DEFAULT '0',
  `created_at`            DATETIME     DEFAULT CURRENT_TIMESTAMP,
  `product_id`            VARCHAR(36)  DEFAULT NULL,
  `estimated_price`       INT          DEFAULT NULL,
  `store_id`              VARCHAR(36)  DEFAULT NULL,
  PRIMARY KEY (`list_item_id`),
  KEY `fk_listitem_shoppinglist` (`shopping_list_id`),
  CONSTRAINT `fk_listitem_shoppinglist`
    FOREIGN KEY (`shopping_list_id`) REFERENCES `ShoppingList` (`shopping_list_id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- RoutePlan  (→ User, Market)
-- NOTE: shopping_list_id, estimated_minutes, distance_meters were added via
-- ALTER TABLE; shopping_list_id is nullable to match Railway DB state.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `RoutePlan` (
  `route_plan_id`    VARCHAR(36) NOT NULL,
  `user_id`          VARCHAR(36) NOT NULL,
  `market_id`        VARCHAR(36) NOT NULL,
  `route_json`       JSON        NOT NULL,
  `created_at`       DATETIME    DEFAULT CURRENT_TIMESTAMP,
  `shopping_list_id` VARCHAR(36) DEFAULT NULL,
  `estimated_minutes` INT        DEFAULT NULL,
  `distance_meters`  INT         DEFAULT NULL,
  PRIMARY KEY (`route_plan_id`),
  KEY `fk_routeplan_user`   (`user_id`),
  KEY `fk_routeplan_market` (`market_id`),
  CONSTRAINT `fk_routeplan_user`
    FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_routeplan_market`
    FOREIGN KEY (`market_id`) REFERENCES `Market` (`market_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Notification  (→ User)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Notification` (
  `notification_id`  VARCHAR(36)  NOT NULL,
  `user_id`          VARCHAR(36)  NOT NULL,
  `type`             VARCHAR(50)  NOT NULL,
  `title`            VARCHAR(200) NOT NULL,
  `body`             TEXT         DEFAULT NULL,
  `target_screen_id` VARCHAR(50)  DEFAULT NULL,
  `target_type`      VARCHAR(50)  DEFAULT NULL,
  `target_id`        VARCHAR(36)  DEFAULT NULL,
  `is_read`          TINYINT(1)   NOT NULL DEFAULT '0',
  `send_status`      VARCHAR(20)  DEFAULT NULL,
  `created_at`       DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`),
  KEY `fk_notification_user` (`user_id`),
  CONSTRAINT `fk_notification_user`
    FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- ProductPriceHistory  (→ Product)  — 가격 변경 이력 (Phase 2)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `ProductPriceHistory` (
  `history_id`   VARCHAR(36)  NOT NULL,
  `product_id`   VARCHAR(36)  NOT NULL,
  `old_price`    INT          NOT NULL,
  `new_price`    INT          NOT NULL,
  `reason`       ENUM('manual','kamis','system') NOT NULL DEFAULT 'manual',
  `reference_id` VARCHAR(36)  DEFAULT NULL COMMENT 'KAMIS market_price_id 등',
  `created_at`   DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`history_id`),
  KEY `fk_pph_product` (`product_id`),
  CONSTRAINT `fk_pph_product`
    FOREIGN KEY (`product_id`) REFERENCES `Product` (`product_id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='상품 가격 변경 이력';

-- -----------------------------------------------------------------------------
-- Preorder  (→ User, Store)  — Phase 2 (활성화)
CREATE TABLE IF NOT EXISTS `Preorder` (
  `preorder_id`  VARCHAR(36)  NOT NULL,
  `user_id`      VARCHAR(36)  NOT NULL,
  `store_id`     VARCHAR(36)  NOT NULL,
  `product_name` VARCHAR(100) NOT NULL,
  `qty`          INT          NOT NULL,
  `status`       ENUM('requested','confirmed','ready','cancelled') NOT NULL DEFAULT 'requested',
  `created_at`   DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`preorder_id`),
  KEY `fk_preorder_user`  (`user_id`),
  KEY `fk_preorder_store` (`store_id`),
  CONSTRAINT `fk_preorder_user`
    FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_preorder_store`
    FOREIGN KEY (`store_id`) REFERENCES `Store` (`store_id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
