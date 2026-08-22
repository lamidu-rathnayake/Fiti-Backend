-- Truncate all tables in the database
-- We use CASCADE to automatically handle foreign key dependencies

TRUNCATE TABLE 
    clients,
    tailors,
    measurement_profile,
    user_roles,
    shops,
    shop_images,
    clothing_requests,
    clothing_request_images,
    measurements,
    shop_requests,
    bids,
    orders,
    payments,
    ratings,
    favorite_shops,
    notifications
CASCADE;
