-- Fiti database reset and creation script
-- PostgreSQL 14+ / Supabase
-- WARNING: This permanently deletes all Fiti business data.
-- Run this entire script only against the intended database.

BEGIN;

-- Remove tables first so dependent types and constraints can be recreated cleanly.
DROP TABLE IF EXISTS
    role_section_grants,
    section_sub_sections,
    sub_sections,
    sections,
    user_roles,
    roles,
    ratings,
    payments,
    orders,
    bids,
    shop_requests,
    measurements,
    clothing_request_images,
    clothing_requests,
    favorite_shops,
    notifications,
    shop_images,
    shops,
    measurement_profile,
    clients,
    tailors
CASCADE;

DROP TYPE IF EXISTS
    gender_enum,
    fabric_status_enum,
    clothing_request_status_enum,
    clothing_request_type_enum,
    shop_request_status_enum,
    order_status_enum,
    payment_method_enum,
    payment_status_enum,
    service_type_enum
CASCADE;

-- The ORM uses native_enum=False, so enum values are constrained VARCHAR fields.

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Identity extensions. Passwords and Firebase tokens remain in Firebase Auth.
CREATE TABLE clients (
    id           VARCHAR(128) PRIMARY KEY,
    display_name TEXT,
    email        TEXT,
    photo_url    VARCHAR(2048),
    phone        VARCHAR(20),
    city         VARCHAR(100),
    address      VARCHAR(255),
    latitude     NUMERIC(9,6),
    longitude    NUMERIC(9,6),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tailors (
    id           VARCHAR(128) PRIMARY KEY,
    display_name TEXT,
    email        TEXT,
    photo_url    VARCHAR(2048),
    nic_front    VARCHAR(2048),
    nic_rear     VARCHAR(2048),
    is_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    phone        VARCHAR(20),
    city         VARCHAR(100),
    address      VARCHAR(255),
    latitude     NUMERIC(9,6),
    longitude    NUMERIC(9,6),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE measurement_profile (
    measurement_id SERIAL PRIMARY KEY,
    client_id      VARCHAR(128) NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
    chest          NUMERIC(5,2),
    waist          NUMERIC(5,2),
    shoulder       NUMERIC(5,2),
    sleeve         NUMERIC(5,2),
    neck           NUMERIC(5,2),
    hip            NUMERIC(5,2),
    inseam         NUMERIC(5,2),
    length         NUMERIC(5,2),
    notes          TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RBAC defaults are seeded below.
CREATE TABLE roles (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE user_roles (
    firebase_uid VARCHAR(128) NOT NULL,
    role_id      INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (firebase_uid, role_id)
);

CREATE TABLE shops (
    shop_id              SERIAL PRIMARY KEY,
    tailor_id            VARCHAR(128) NOT NULL REFERENCES tailors(id) ON DELETE CASCADE,
    shop_name            VARCHAR(150) NOT NULL,
    specialty            TEXT,
    shop_bio             TEXT,
    shop_address         VARCHAR(255),
    city                 VARCHAR(100),
    contact_number       VARCHAR(20),
    registration_number  VARCHAR(100),
    latitude             NUMERIC(9,6),
    longitude            NUMERIC(9,6),
    average_rating       NUMERIC(3,2) NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE shop_images (
    image_id   SERIAL PRIMARY KEY,
    shop_id    INTEGER NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    image_url  VARCHAR(2048) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE clothing_requests (
    request_id             SERIAL PRIMARY KEY,
    client_id              VARCHAR(128) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    target_date            DATE,
    target_budget          NUMERIC(10,2) CHECK (target_budget IS NULL OR target_budget > 0),
    clothing_category      VARCHAR(100),
    gender                 VARCHAR(20) CHECK (gender IN ('male', 'female', 'unisex')),
    fabric_status          VARCHAR(30) CHECK (fabric_status IN ('client_provided', 'shop_provides')),
    description            TEXT,
    voice_note_url         VARCHAR(2048),
    service_type           VARCHAR(30) NOT NULL DEFAULT 'online' CHECK (service_type IN ('online', 'physical_visit')),
    request_type           VARCHAR(30) NOT NULL DEFAULT 'direct' CHECK (request_type IN ('direct', 'bidding')),
    request_location       VARCHAR(255),
    status                 VARCHAR(30) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled')),
    measurement_profile_id INTEGER REFERENCES measurement_profile(measurement_id) ON DELETE SET NULL,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE clothing_request_images (
    image_id   SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES clothing_requests(request_id) ON DELETE CASCADE,
    image_url  VARCHAR(2048) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- One inline measurement record may be attached to each clothing request.
CREATE TABLE measurements (
    measurement_id SERIAL PRIMARY KEY,
    request_id     INTEGER NOT NULL UNIQUE REFERENCES clothing_requests(request_id) ON DELETE CASCADE,
    chest          NUMERIC(5,2) CHECK (chest IS NULL OR chest > 0),
    waist          NUMERIC(5,2) CHECK (waist IS NULL OR waist > 0),
    shoulder       NUMERIC(5,2) CHECK (shoulder IS NULL OR shoulder > 0),
    sleeve         NUMERIC(5,2) CHECK (sleeve IS NULL OR sleeve > 0),
    neck           NUMERIC(5,2) CHECK (neck IS NULL OR neck > 0),
    hip            NUMERIC(5,2) CHECK (hip IS NULL OR hip > 0),
    inseam         NUMERIC(5,2) CHECK (inseam IS NULL OR inseam > 0),
    length         NUMERIC(5,2) CHECK (length IS NULL OR length > 0),
    notes          TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE shop_requests (
    shop_request_id SERIAL PRIMARY KEY,
    request_id      INTEGER NOT NULL REFERENCES clothing_requests(request_id) ON DELETE CASCADE,
    shop_id         INTEGER NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    offered_price   NUMERIC(10,2) CHECK (offered_price IS NULL OR offered_price > 0),
    status          VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'quoted', 'accepted', 'rejected', 'withdrawn')),
    response_date   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (request_id, shop_id)
);

CREATE TABLE bids (
    bid_id          SERIAL PRIMARY KEY,
    shop_request_id INTEGER NOT NULL REFERENCES shop_requests(shop_request_id) ON DELETE CASCADE,
    bid_amount      NUMERIC(10,2) NOT NULL CHECK (bid_amount > 0),
    message         TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    order_id        SERIAL PRIMARY KEY,
    shop_request_id INTEGER NOT NULL UNIQUE REFERENCES shop_requests(shop_request_id) ON DELETE CASCADE,
    order_status    VARCHAR(30) NOT NULL DEFAULT 'in_progress' CHECK (order_status IN ('in_progress', 'completed', 'cancelled')),
    accepted_price  NUMERIC(10,2) NOT NULL CHECK (accepted_price > 0),
    started_date    DATE,
    completed_date  DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE payments (
    payment_id     SERIAL PRIMARY KEY,
    order_id       INTEGER NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    amount         NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(30) CHECK (payment_method IN ('cash', 'card', 'bank_transfer', 'mobile_wallet')),
    payment_status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),
    payment_date   TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ratings (
    rating_id SERIAL PRIMARY KEY,
    order_id  INTEGER NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    client_id VARCHAR(128) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    shop_id   INTEGER NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    rating    SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review    TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE favorite_shops (
    favorite_id SERIAL PRIMARY KEY,
    client_id   VARCHAR(128) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    shop_id     INTEGER NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (client_id, shop_id)
);

CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    firebase_uid    VARCHAR(128) NOT NULL,
    title           VARCHAR(150) NOT NULL,
    message         TEXT,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Query indexes.
CREATE INDEX idx_shops_tailor_id ON shops(tailor_id);
CREATE INDEX idx_shop_images_shop_id ON shop_images(shop_id);
CREATE INDEX idx_clothing_requests_client ON clothing_requests(client_id);
CREATE INDEX idx_clothing_requests_status ON clothing_requests(status);
CREATE INDEX idx_clothing_requests_measurement_profile ON clothing_requests(measurement_profile_id);
CREATE INDEX idx_clothing_request_images_request ON clothing_request_images(request_id);
CREATE INDEX idx_shop_requests_request ON shop_requests(request_id);
CREATE INDEX idx_shop_requests_shop_status ON shop_requests(shop_id, status);
CREATE INDEX idx_bids_shop_request ON bids(shop_request_id);
CREATE INDEX idx_orders_shop_request ON orders(shop_request_id);
CREATE INDEX idx_ratings_shop ON ratings(shop_id);
CREATE INDEX idx_favorite_shops_shop ON favorite_shops(shop_id);
CREATE INDEX idx_notifications_user ON notifications(firebase_uid);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);

-- Automatically maintain update timestamps.
CREATE TRIGGER trg_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_tailors_updated_at BEFORE UPDATE ON tailors FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_measurement_profile_updated_at BEFORE UPDATE ON measurement_profile FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_shops_updated_at BEFORE UPDATE ON shops FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_clothing_requests_updated_at BEFORE UPDATE ON clothing_requests FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_measurements_updated_at BEFORE UPDATE ON measurements FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_shop_requests_updated_at BEFORE UPDATE ON shop_requests FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Default RBAC data required by registration and role lookup.
INSERT INTO roles (name) VALUES ('client'), ('tailor'), ('admin');

COMMIT;

-- Verify the reset.
SELECT id, name FROM roles ORDER BY id;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'clients', 'tailors', 'measurement_profile', 'roles', 'user_roles',
      'shops', 'clothing_requests', 'measurements', 'shop_requests',
      'bids', 'orders', 'payments', 'ratings', 'favorite_shops', 'notifications'
  )
ORDER BY table_name;
