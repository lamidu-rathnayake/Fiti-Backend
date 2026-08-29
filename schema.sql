-- =========================================================
-- Fiti — Smart Tailoring & Custom Fashion Platform Database Schema
-- Combined Business Domain + Auth/RBAC Schema
-- Target: PostgreSQL 14+
-- =========================================================

-- ---------------------------------------------------------
-- 1. ENUM TYPES
-- ---------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE gender_enum AS ENUM ('male', 'female', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE fabric_status_enum AS ENUM ('client_provided', 'shop_provides');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE clothing_request_status_enum AS ENUM ('open', 'in_progress', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE clothing_request_type_enum AS ENUM ('direct', 'bidding');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE shop_request_status_enum AS ENUM ('pending', 'quoted', 'accepted', 'rejected', 'withdrawn');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE order_status_enum AS ENUM ('in_progress', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_method_enum AS ENUM ('cash', 'card', 'bank_transfer', 'mobile_wallet');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_status_enum AS ENUM ('pending', 'paid', 'failed', 'refunded');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- NEW: Supports the hybrid online/physical-visit operational toggle
DO $$ BEGIN
    CREATE TYPE service_type_enum AS ENUM ('online', 'physical_visit');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ---------------------------------------------------------
-- 2. UTILITY: auto-maintain updated_at on row change
-- ---------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------
-- 3. PROFILE EXTENSIONS (Firebase-backed identity)
-- ---------------------------------------------------------
-- NOTE: Full user identity (name, email, password, auth provider) lives in
-- Firebase Auth. PostgreSQL only stores role-specific profile extensions.
-- The `id` column in clients/tailors(tailors) holds the Firebase Auth UID directly
-- with NO foreign key to a users table (there is no users table).

CREATE TABLE IF NOT EXISTS clients (
    id            VARCHAR(128) PRIMARY KEY,               -- Firebase Auth UID
    display_name  TEXT DEFAULT NULL,                      -- Extracted from JWT
    email         TEXT DEFAULT NULL,                      -- Extracted from JWT
    photo_url     TEXT DEFAULT NULL,                      -- Extracted from JWT
    phone         TEXT DEFAULT NULL,                      -- Contact phone number (migrated from Firestore)
    city          TEXT DEFAULT NULL,                      -- City (migrated from Firestore)
    address       TEXT DEFAULT NULL,                      -- Street address (migrated from Firestore)
    latitude      NUMERIC(9,6),
    longitude     NUMERIC(9,6),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tailors (
    id           VARCHAR(128) PRIMARY KEY,              -- Firebase Auth UID
    display_name TEXT DEFAULT NULL,                     -- Extracted from JWT
    email        TEXT DEFAULT NULL,                     -- Extracted from JWT
    photo_url    TEXT DEFAULT NULL,                     -- Extracted from JWT
    nic_front    VARCHAR(2048),                          -- Cloud storage URL
    nic_rear     VARCHAR(2048),                          -- Cloud storage URL
    is_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    phone        TEXT DEFAULT NULL,                      -- Contact phone number (migrated from Firestore)
    city         TEXT DEFAULT NULL,                      -- City (migrated from Firestore)
    address      TEXT DEFAULT NULL,                      -- Street address (migrated from Firestore)
    latitude     NUMERIC(9,6),
    longitude    NUMERIC(9,6),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- References clients.id (Firebase UID) — no dependency on a users table
CREATE TABLE IF NOT EXISTS measurement_profile (
    measurement_id  SERIAL PRIMARY KEY,
    client_id       VARCHAR(128) NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
    chest           NUMERIC(5,2),
    waist           NUMERIC(5,2),
    shoulder        NUMERIC(5,2),
    sleeve          NUMERIC(5,2),
    neck            NUMERIC(5,2),
    hip             NUMERIC(5,2),
    inseam          NUMERIC(5,2),
    length          NUMERIC(5,2),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------
-- 4. RBAC (roles, sections, sub-sections, grants)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS user_roles (
    -- firebase_uid stores the Firebase Auth UID — no FK since users table does not exist in PostgreSQL
    firebase_uid  VARCHAR(128) NOT NULL,
    role_id       INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (firebase_uid, role_id)
);

CREATE TABLE IF NOT EXISTS sections (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    route_name  VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS role_section_grants (
    role_id     INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    section_id  INT NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, section_id)
);

CREATE TABLE IF NOT EXISTS sub_sections (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    component_id  VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS section_sub_sections (
    section_id      INT NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    sub_section_id  INT NOT NULL REFERENCES sub_sections(id) ON DELETE CASCADE,
    PRIMARY KEY (section_id, sub_section_id)
);

-- ---------------------------------------------------------
-- 5. SHOP / TAILOR DOMAIN
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS shops (
    shop_id              SERIAL PRIMARY KEY,
    tailor_id            VARCHAR(128) NOT NULL REFERENCES tailors(id) ON DELETE CASCADE,
    shop_name            VARCHAR(150) NOT NULL,
    specialty            TEXT DEFAULT NULL,              -- Tailor specialty (migrated from Firestore)
    shop_bio             TEXT,
    shop_address         VARCHAR(255),
    city                 VARCHAR(100),
    contact_number       VARCHAR(20),
    registration_number VARCHAR(100),
    latitude             NUMERIC(9,6),
    longitude            NUMERIC(9,6),
    average_rating       NUMERIC(3,2) NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shop_images (
    image_id    SERIAL PRIMARY KEY,
    shop_id     INT NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    image_url   VARCHAR(2048) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------
-- 6. ORDER FLOW: request -> broadcast -> bid -> order -> payment -> rating
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS clothing_requests (
    request_id          SERIAL PRIMARY KEY,
    client_id           VARCHAR(128) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    target_date         DATE,
    target_budget       NUMERIC(10,2),
    clothing_category   VARCHAR(100),
    gender              gender_enum,
    fabric_status       fabric_status_enum,
    description         TEXT,
    -- NEW: URL to Firebase Storage / Azure Blob for recorded voice instructions
    voice_note_url      VARCHAR(2048),
    -- NEW: Operational toggle — client chooses online or physical shop visit
    service_type        service_type_enum NOT NULL DEFAULT 'online',
    -- NEW: Direct vs Bidding distinction
    request_type        clothing_request_type_enum NOT NULL DEFAULT 'direct',
    request_location    VARCHAR(255),
    status              clothing_request_status_enum NOT NULL DEFAULT 'open',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- NEW: Stores multiple design inspiration images (Pinterest screenshots, etc.) per request
-- Files are uploaded to cloud storage first; only the URL is stored here.
CREATE TABLE IF NOT EXISTS clothing_request_images (
    image_id    SERIAL PRIMARY KEY,
    request_id  INT NOT NULL REFERENCES clothing_requests(request_id) ON DELETE CASCADE,
    image_url   VARCHAR(2048) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id  SERIAL PRIMARY KEY,
    -- FIXED: references clothing_requests(request_id) — correct PK column name
    request_id      INT NOT NULL UNIQUE REFERENCES clothing_requests(request_id) ON DELETE CASCADE,
    chest           NUMERIC(5,2),
    waist           NUMERIC(5,2),
    shoulder        NUMERIC(5,2),
    sleeve          NUMERIC(5,2),
    neck            NUMERIC(5,2),
    hip             NUMERIC(5,2),
    inseam          NUMERIC(5,2),
    length          NUMERIC(5,2),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shop_requests (
    shop_request_id    SERIAL PRIMARY KEY,
    -- FIXED: references clothing_requests(request_id) — correct PK column name
    request_id         INT NOT NULL REFERENCES clothing_requests(request_id) ON DELETE CASCADE,
    shop_id            INT NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    offered_price      NUMERIC(10,2),
    status             shop_request_status_enum NOT NULL DEFAULT 'pending',
    response_date      TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (request_id, shop_id)
);

CREATE TABLE IF NOT EXISTS bids (
    bid_id           SERIAL PRIMARY KEY,
    shop_request_id  INT NOT NULL REFERENCES shop_requests(shop_request_id) ON DELETE CASCADE,
    bid_amount       NUMERIC(10,2) NOT NULL CHECK (bid_amount >= 0),
    message          TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    order_id         SERIAL PRIMARY KEY,
    shop_request_id  INT NOT NULL UNIQUE REFERENCES shop_requests(shop_request_id) ON DELETE CASCADE,
    order_status     order_status_enum NOT NULL DEFAULT 'in_progress',
    accepted_price   NUMERIC(10,2) NOT NULL,
    started_date     DATE,
    completed_date   DATE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id      SERIAL PRIMARY KEY,
    order_id        INT NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    amount          NUMERIC(10,2) NOT NULL,
    payment_method  payment_method_enum,
    payment_status  payment_status_enum NOT NULL DEFAULT 'pending',
    payment_date    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ratings (
    rating_id   SERIAL PRIMARY KEY,
    order_id    INT NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    client_id   VARCHAR(128) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    shop_id     INT NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    rating      SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review      TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------
-- 7. SUPPORTING TABLES
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS favorite_shops (
    favorite_id  SERIAL PRIMARY KEY,
    client_id    VARCHAR(128) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    shop_id      INT NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (client_id, shop_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id  SERIAL PRIMARY KEY,
    -- firebase_uid stores the Firebase Auth UID — no FK since users table does not exist in PostgreSQL
    firebase_uid     VARCHAR(128) NOT NULL,
    title            VARCHAR(150) NOT NULL,
    message          TEXT,
    is_read          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------
-- 8. INDEXES (FK columns not already indexed by a PK/UNIQUE)
-- ---------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_shops_tailor_id                ON shops(tailor_id);
CREATE INDEX IF NOT EXISTS idx_shop_images_shop_id            ON shop_images(shop_id);
CREATE INDEX IF NOT EXISTS idx_clothing_requests_client       ON clothing_requests(client_id);
CREATE INDEX IF NOT EXISTS idx_clothing_requests_status       ON clothing_requests(status);
CREATE INDEX IF NOT EXISTS idx_clothing_request_images_req_id ON clothing_request_images(request_id);
CREATE INDEX IF NOT EXISTS idx_shop_requests_request_id       ON shop_requests(request_id);
CREATE INDEX IF NOT EXISTS idx_shop_requests_shop_id          ON shop_requests(shop_id);
CREATE INDEX IF NOT EXISTS idx_bids_shop_request_id           ON bids(shop_request_id);
CREATE INDEX IF NOT EXISTS idx_ratings_shop_id                ON ratings(shop_id);
CREATE INDEX IF NOT EXISTS idx_favorite_shops_shop_id         ON favorite_shops(shop_id);
CREATE INDEX IF NOT EXISTS idx_notifications_firebase_uid     ON notifications(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id             ON user_roles(role_id);

-- ---------------------------------------------------------
-- 9. TRIGGERS: keep updated_at current
-- ---------------------------------------------------------
DROP TRIGGER IF EXISTS trg_clients_updated_at ON clients;
CREATE TRIGGER trg_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_tailors_updated_at ON tailors;
CREATE TRIGGER trg_tailors_updated_at BEFORE UPDATE ON tailors FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_shops_updated_at ON shops;
CREATE TRIGGER trg_shops_updated_at BEFORE UPDATE ON shops FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_clothing_requests_updated_at ON clothing_requests;
CREATE TRIGGER trg_clothing_requests_updated_at BEFORE UPDATE ON clothing_requests FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_measurements_updated_at ON measurements;
CREATE TRIGGER trg_measurements_updated_at BEFORE UPDATE ON measurements FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_shop_requests_updated_at ON shop_requests;
CREATE TRIGGER trg_shop_requests_updated_at BEFORE UPDATE ON shop_requests FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_orders_updated_at ON orders;
CREATE TRIGGER trg_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------
-- 10. SEED DATA (Default Roles & Sections)
-- ---------------------------------------------------------
INSERT INTO roles (name) VALUES ('client'), ('tailor'), ('admin')
ON CONFLICT (name) DO NOTHING;

INSERT INTO sections (name, route_name) VALUES
  ('Home', '/home'),
  ('Client Dashboard', '/client/dashboard'),
  ('Tailor Dashboard', '/tailor/dashboard'),
  ('Admin Console', '/admin/console')
ON CONFLICT (name) DO NOTHING;

-- Seed role_section_grants mapping
INSERT INTO role_section_grants (role_id, section_id)
SELECT r.id, s.id
FROM roles r
CROSS JOIN sections s
WHERE (r.name = 'client' AND s.name IN ('Home', 'Client Dashboard'))
   OR (r.name = 'tailor' AND s.name IN ('Home', 'Tailor Dashboard'))
   OR (r.name = 'tailor' AND s.name IN ('Home', 'Tailor Dashboard'))
   OR (r.name = 'admin' AND s.name IN ('Home', 'Admin Console'))
ON CONFLICT (role_id, section_id) DO NOTHING;

