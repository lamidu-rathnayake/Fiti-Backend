# Backend Bug Report: Missing `user_roles` Insertion

**To the Backend Agent:**
There is a critical bug in the profile creation flow that is breaking the frontend's Google Login functionality. Please read this brief and fix the endpoints accordingly.

## The Bug: Infinite Redirect on Existing User Login
When an existing user logs in using Google (or email/password), the frontend calls `GET /api/v1/auth/me/role` to determine if they are a client or a tailor so it can route them to the correct dashboard.

Currently, this endpoint is returning `404 Not Found` for users who have *already completed registration*. Because it returns 404, the frontend assumes the user's profile doesn't exist and redirects them back to the `/onboarding` page in an infinite loop.

## The Root Cause
When the frontend registers a new user, it calls one of two endpoints:
- `POST /api/v1/profiles/client`
- `POST /api/v1/profiles/tailor`

**The backend is successfully inserting the profile into the `clients` or `tailors` table, BUT it is FAILING to insert the corresponding role into the `user_roles` table.**

Because the `user_roles` table remains empty for this user, `GET /api/v1/auth/me/role` (which joins the `user_roles` and `roles` tables based on the `firebase_uid`) cannot find the role and returns 404.

## How to Fix It
You need to modify the implementation of the `POST /api/v1/profiles/client` and `POST /api/v1/profiles/tailor` endpoints. 

In the same database transaction where you insert into the `clients` or `tailors` table, you **must** also execute an atomic insert into the `user_roles` table.

**Expected SQL logic during `POST /api/v1/profiles/client`:**
```sql
-- 1. Insert profile
INSERT INTO clients (id, ...) VALUES (firebase_uid, ...);

-- 2. Fetch the role ID for 'client'
SELECT id FROM roles WHERE name = 'client';

-- 3. Insert the mapping
INSERT INTO user_roles (firebase_uid, role_id) VALUES (firebase_uid, fetched_role_id);
```

*(Repeat the exact same logic for the Tailor endpoint, but using `name = 'tailor'`)*

## Verification
To verify your fix works:
1. Hit the POST endpoint to create a new client or tailor profile.
2. Directly query the database: `SELECT * FROM user_roles WHERE firebase_uid = 'test_uid';` -> It should return exactly 1 row.
3. Hit `GET /api/v1/auth/me/role` with that user's token -> It should return `{ "role": "client" }` (or tailor) with a 200 OK, not a 404.
