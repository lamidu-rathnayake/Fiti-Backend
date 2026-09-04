-- Fiti migration: shop service gigs
-- Run once against the existing PostgreSQL database.

CREATE TABLE IF NOT EXISTS gigs (
    gig_id         SERIAL PRIMARY KEY,
    shop_id        INT NOT NULL REFERENCES shops(shop_id) ON DELETE CASCADE,
    title          VARCHAR(150) NOT NULL,
    description    TEXT NOT NULL,
    price          NUMERIC(12,2) NOT NULL CHECK (price > 0),
    delivery_time  VARCHAR(100),
    category       VARCHAR(100),
    image_url      VARCHAR(2048),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gigs_shop_id ON gigs(shop_id);

DROP TRIGGER IF EXISTS gigs_set_updated_at ON gigs;
CREATE TRIGGER gigs_set_updated_at
    BEFORE UPDATE ON gigs
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
