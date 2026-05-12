-- =============================================================
-- Story 테이블 추가 (SPEC.md ADR-04 반영)
-- 상인 스토리 LLM 생성 결과를 영구 저장하고 게시·조회 가능하게 함
-- =============================================================

USE market_mvp;

CREATE TABLE IF NOT EXISTS Story (
  story_id          VARCHAR(36)  NOT NULL,
  store_id          VARCHAR(36)  NOT NULL,
  merchant_id       VARCHAR(36)  DEFAULT NULL,
  title             VARCHAR(200) DEFAULT NULL,
  content           TEXT         NOT NULL,
  content_short     TEXT         DEFAULT NULL,
  content_normal    TEXT         DEFAULT NULL,
  content_detailed  TEXT         DEFAULT NULL,
  tone              VARCHAR(50)  DEFAULT '친근한',
  selected_length   ENUM('short','normal','detailed') NOT NULL DEFAULT 'normal',
  hashtags_json     TEXT         DEFAULT NULL COMMENT '["#태그", ...] JSON 문자열',
  interview_text    TEXT         DEFAULT NULL,
  fallback_mode     TINYINT(1)   NOT NULL DEFAULT 0,
  is_published      TINYINT(1)   NOT NULL DEFAULT 0,
  published_at      DATETIME     DEFAULT NULL,
  deleted_at        DATETIME     DEFAULT NULL,
  updated_at        DATETIME     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (story_id),
  KEY ix_story_store (store_id, deleted_at, is_published),
  KEY ix_story_merchant (merchant_id),
  CONSTRAINT fk_story_store
    FOREIGN KEY (store_id) REFERENCES Store (store_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='상인 스토리 (LLM 생성 결과 + 게시 상태 관리)';
