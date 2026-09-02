-- Truncate only transactional business data
-- This preserves user accounts (clients/tailors), roles, shops, and measurement profiles
-- We use CASCADE to automatically handle foreign key dependencies within these tables

TRUNCATE TABLE 
    clothing_requests,
    clothing_request_images,
    -- measurements,
    shop_requests,
    bids,
    orders,
    payments,
    ratings,
    notifications
CASCADE;
