# FRONTEND AGENT HANDOFF — Fiti Backend Compatibility & Registration Audit

> **Purpose:** This is the single authoritative handoff document from the frontend agent to the backend developer.
> It covers the Firestore removal migration, all updated endpoint contracts, the full registration flow wiring,
> and the critical `user_roles` requirements that drive role-based access control.
>
> **Frontend version:** All onboarding & auth flows  
> **Status:** Frontend changes complete — backend changes required before release  
> **Last updated:** 2026-08-21

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Database Migrations](#2-database-migrations)
3. [Authentication Architecture](#3-authentication-architecture)
4. [Client Registration Flow](#4-client-registration-flow)
5. [Tailor Registration Flow](#5-tailor-registration-flow)
6. [Critical `user_roles` Wiring](#6-critical-user_roles-wiring)
7. [Role Lookup Endpoint](#7-role-lookup-endpoint)
8. [Updated Endpoint Contracts](#8-updated-endpoint-contracts)
9. [Auth Middleware — No Changes Required](#9-auth-middleware--no-changes-required)
10. [Data Gap — JWT Claims](#10-data-gap--jwt-claims)
11. [NIC Image Upload — Current State](#11-nic-image-upload--current-state)
12. [What Was Removed (Frontend)](#12-what-was-removed-frontend)
13. [Master Verification Checklist](#13-master-verification-checklist)
14. [Frontend Source File Reference](#14-frontend-source-file-reference)

---

## 1. Architecture Overview

### Context

The frontend previously used a Firestore `users` collection as a fast-read cache for `role`, `phone`, `city`, `address`, and `specialty`. This collection has been **removed entirely**. Firebase is now used **exclusively for authentication** (identity tokens, session management). All business and profile data lives in Supabase PostgreSQL via the backend API.

**The frontend still uses Firebase ID tokens as Bearer tokens for all authenticated requests — the auth middleware is unchanged.**

The Firebase UID is **never sent in the request body**. The backend must always extract it from the signed JWT (`uid` claim) and use it as the primary key (`id`) when inserting into `clients` or `tailors`.

### System Map

```
User fills form
      │
      ▼
Firebase Auth  ──► createUserWithEmailAndPassword()
      │               Sets: UID, email, password hash
      │
      ▼
Firebase updateProfile()
      │               Sets: displayName, photoURL
      │
      ▼
firebaseUser.getIdToken(true)   ← FORCE REFRESH (critical)
      │               Token now carries updated displayName + photoURL claims
      │
      ▼
Backend API  ──►  Bearer {idToken}  in Authorization header
      │               Backend decodes → extracts firebase_uid from token
      │
      ▼
 Supabase PostgreSQL
 ┌────────────┐    ┌────────────┐    ┌──────────────────┐
 │  clients   │    │  tailors   │    │   user_roles     │
 └────────────┘    └────────────┘    └──────────────────┘
```

**Key principle:** The frontend NEVER sends `uid` in the JSON body. The backend must extract it from the decoded Firebase JWT (`sub` claim = Firebase UID).

### Admin Backend Note

The admin stack is a **completely separate backend project** sharing the same Firebase project and Supabase database. This backend does **not** handle admin operations. There are no admin endpoints here — only `client` and `tailor` roles are assigned through this backend's registration flow.

---

## 2. Database Migrations

Run all three migrations in order against your Supabase instance.

### 2a. `clients` table — add contact and profile fields

```sql
ALTER TABLE clients
  ADD COLUMN IF NOT EXISTS display_name TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS email        TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS photo_url    TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS phone        TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS city         TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS address      TEXT DEFAULT NULL;
```

### 2b. `tailors` table — add contact and profile fields

```sql
ALTER TABLE tailors
  ADD COLUMN IF NOT EXISTS display_name TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS email        TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS photo_url    TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS phone        TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS city         TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS address      TEXT DEFAULT NULL;
```

### 2c. `shops` table — add specialty field

```sql
ALTER TABLE shops
  ADD COLUMN IF NOT EXISTS specialty TEXT DEFAULT NULL;
```

> `specialty` was previously only written to Firestore. It is a shop-level attribute (e.g. "Bridal wear", "Alterations") and belongs on the `shops` table.

> **All new columns are nullable.** Do not add `NOT NULL` constraints.

### 2d. `roles` table — seed data (critical)

The `roles` table **must** contain these rows (all lowercase) before any user can register:

```sql
INSERT INTO roles (name) VALUES ('client'), ('tailor'), ('admin')
ON CONFLICT (name) DO NOTHING;
```

> ⚠️ Role names must be **lowercase** (`'client'`, `'tailor'`). The backend queries with exact string match. If names are capitalised (e.g. `'Client'`), `get_role_by_name` returns `None` and `user_roles` will silently not be populated.

---

## 3. Authentication Architecture

| JWT Claim | Maps to DB column |
|---|---|
| `sub` | `id` (PK in `clients` / `tailors`) |
| `name` | `display_name` |
| `email` | `email` |
| `picture` | `photo_url` |

> **The `getIdToken(true)` force-refresh** on the frontend ensures `name` and `picture` are current in the token at the moment the profile creation call is made. If the backend reads these claims lazily or caches the token, `display_name` and `photo_url` may be empty.

### Data NOT in the JSON body (comes from Firebase token)

| Data point | Source | How backend gets it |
|---|---|---|
| `firebase_uid` | Firebase JWT `sub` claim | Decoded from Bearer token |
| `email` | Firebase JWT `email` claim | Decoded from Bearer token |
| `display_name` | Firebase JWT `name` claim | Decoded from Bearer token (set via `updateProfile`) |
| `photo_url` | Firebase JWT `picture` claim | Decoded from Bearer token (set via `updateProfile`) |

---

## 4. Client Registration Flow

### Endpoint

```
POST /api/v1/profiles/client
Authorization: Bearer <firebase_id_token>
Content-Type: application/json
```

### JSON Body Sent by Frontend

```json
{
  "phone":     "string | null",
  "city":      "string | null",
  "address":   "string | null",
  "latitude":  "number | null",
  "longitude": "number | null"
}
```

### Required `clients` Table Compatibility

| Column | Type | Nullable | Value Source | Status |
|---|---|---|---|---|
| `id` | `varchar` / `text` | NOT NULL (PK) | `firebase_uid` from token | ⚠️ Backend must extract from token |
| `display_name` | `text` | nullable | `name` claim from token | ⚠️ Backend must extract from token |
| `email` | `text` | nullable | `email` claim from token | ⚠️ Backend must extract from token |
| `photo_url` | `text` | nullable | `picture` claim from token | ⚠️ Backend must extract from token |
| `phone` | `text` | nullable | JSON body `phone` | ✅ Frontend sends |
| `city` | `text` | nullable | JSON body `city` | ✅ Frontend sends |
| `address` | `text` | nullable | JSON body `address` | ✅ Frontend sends |
| `latitude` | `numeric` | nullable | JSON body `latitude` | ✅ Frontend sends |
| `longitude` | `numeric` | nullable | JSON body `longitude` | ✅ Frontend sends |
| `created_at` | `timestamp` | auto | DB default `now()` | ✅ DB auto-fills |
| `updated_at` | `timestamp` | auto | DB default `now()` | ✅ DB auto-fills |

### Required `user_roles` Table Compatibility

| Column | Type | Value | Source |
|---|---|---|---|
| `firebase_uid` | `text` (PK) | User's UID | ⚠️ Backend extracts from token |
| `role_id` | `integer` (FK → `roles.id`) | ID of the `'client'` role | ⚠️ Backend must look up `roles` table for `name='client'` |

> The frontend calls this endpoint once; the backend must atomically insert into **both** `clients` AND `user_roles`.

### Expected HTTP Responses

| Status | Meaning | Frontend handles? |
|---|---|---|
| `201 Created` | Profile created → redirects to `/client/home` | ✅ Yes |
| `409 Conflict` | Profile already exists | ✅ Yes — silently ignored |
| `401 Unauthorized` | Bad/missing token | ✅ Yes — generic error shown |

### Backend Logic Reference

```python
client = Client(
    id=uid,                            # decoded from Bearer token
    display_name=token.get("name"),    # extracted directly from JWT
    email=token.get("email"),          # extracted directly from JWT
    photo_url=token.get("picture"),    # extracted directly from JWT
    phone=body.phone,
    city=body.city,
    address=body.address,
)
db.add(client)
db.add(UserRole(firebase_uid=uid, role_id=CLIENT_ROLE_ID))
```

---

## 5. Tailor Registration Flow

The tailor form is **2-step** but submits everything in a **single sequential call block**. There are **3 API calls** made one after the other.

### Call 1 of 3 — Create Tailor Profile

```
POST /api/v1/profiles/tailor
Authorization: Bearer <firebase_id_token>
Content-Type: application/json
```

#### JSON Body Sent

```json
{
  "phone":     "string | null",
  "city":      "string | null",
  "address":   "string | null",
  "latitude":  "number | null",
  "longitude": "number | null",
  "nic_front": "string (URL) | null",
  "nic_rear":  "string (URL) | null"
}
```

#### Required `tailors` Table Compatibility

| Column | Type | Nullable | Value Source | Status |
|---|---|---|---|---|
| `id` | `varchar` / `text` | NOT NULL (PK) | `firebase_uid` from token | ⚠️ Backend must extract from token |
| `display_name` | `text` | nullable | `name` claim from token | ⚠️ Backend must extract from token |
| `email` | `text` | nullable | `email` claim from token | ⚠️ Backend must extract from token |
| `photo_url` | `text` | nullable | `picture` claim from token | ⚠️ Backend must extract from token |
| `phone` | `text` | nullable | JSON body `phone` | ✅ Frontend sends |
| `city` | `text` | nullable | JSON body `city` | ✅ Frontend sends |
| `address` | `text` | nullable | JSON body `address` | ✅ Frontend sends |
| `latitude` | `numeric` | nullable | JSON body `latitude` | ✅ Frontend sends |
| `longitude` | `numeric` | nullable | JSON body `longitude` | ✅ Frontend sends |
| `nic_front` | `text` | nullable | JSON body `nic_front` (Cloudinary URL) | ✅ Frontend sends |
| `nic_rear` | `text` | nullable | JSON body `nic_rear` (Cloudinary URL) | ✅ Frontend sends |
| `is_verified` | `boolean` | NOT NULL | Backend default `false` | ✅ DB/backend default |
| `created_at` | `timestamp` | auto | DB default `now()` | ✅ DB auto-fills |
| `updated_at` | `timestamp` | auto | DB default `now()` | ✅ DB auto-fills |

#### Required `user_roles` Table Compatibility

| Column | Type | Value | Source |
|---|---|---|---|
| `firebase_uid` | `text` (PK) | User's UID | ⚠️ Backend extracts from token |
| `role_id` | `integer` (FK → `roles.id`) | ID of the `'tailor'` role | ⚠️ Backend must look up `roles` table for `name='tailor'` |

> Same as client — backend must atomically insert into **both** `tailors` AND `user_roles`.

#### Backend Logic Reference

```python
tailor = Tailor(
    id=uid,
    display_name=token.get("name"),
    email=token.get("email"),
    photo_url=token.get("picture"),
    phone=body.phone,
    city=body.city,
    address=body.address,
    nic_front=body.nic_front,
    nic_rear=body.nic_rear,
    is_verified=False,
)
db.add(tailor)
db.add(UserRole(firebase_uid=uid, role_id=TAILOR_ROLE_ID))
```

---

### Call 2 of 3 — Create Shop

```
POST /api/v1/shops/
Authorization: Bearer <firebase_id_token>
Content-Type: application/json
```

#### JSON Body Sent

```json
{
  "shop_name":           "string (required)",
  "specialty":           "string | null",
  "shop_bio":            "string | null",
  "shop_address":        "string | null",
  "city":                "string | null",
  "contact_number":      "string | null",
  "registration_number": "string | null",
  "latitude":            "number | null",
  "longitude":           "number | null"
}
```

> **Address logic:** If "Use my personal address" checkbox is checked (default ON), the shop address/city/phone/lat/lng are copied from Step 1 personal fields.

#### Required `shops` Table Compatibility

| Column | Type | Nullable | Value Source | Status |
|---|---|---|---|---|
| `shop_id` | `integer` | NOT NULL (PK, auto) | DB auto-increment | ✅ DB auto-fills |
| `tailor_id` | `text` (FK) | NOT NULL | `firebase_uid` from token | ⚠️ Backend must extract from token |
| `shop_name` | `text` | NOT NULL | JSON body `shop_name` | ✅ Frontend sends |
| `specialty` | `text` | nullable | JSON body `specialty` | ✅ Frontend sends |
| `shop_bio` | `text` | nullable | JSON body `shop_bio` | ✅ Frontend sends |
| `shop_address` | `text` | nullable | JSON body `shop_address` | ✅ Frontend sends |
| `city` | `text` | nullable | JSON body `city` | ✅ Frontend sends |
| `contact_number` | `text` | nullable | JSON body `contact_number` | ✅ Frontend sends |
| `registration_number` | `text` | nullable | JSON body `registration_number` | ✅ Frontend sends |
| `latitude` | `numeric` | nullable | JSON body `latitude` | ✅ Frontend sends |
| `longitude` | `numeric` | nullable | JSON body `longitude` | ✅ Frontend sends |
| `average_rating` | `numeric` | auto | DB default `0.0` | ✅ DB/backend default |
| `created_at` | `timestamp` | auto | DB default `now()` | ✅ DB auto-fills |
| `updated_at` | `timestamp` | auto | DB default `now()` | ✅ DB auto-fills |

> ⚠️ The backend **must** return `{ shop_id: number, ... }` — the frontend uses `shop.shop_id` immediately in Call 3.

---

### Call 3 of 3 — Add Shop Image (Conditional)

Only called if `shopImageUrl` is present (or falls back to profile `photoURL`).

```
POST /api/v1/shops/{shop_id}/images
Authorization: Bearer <firebase_id_token>
Content-Type: application/json
```

#### JSON Body Sent

```json
{
  "image_url": "string (Cloudinary URL)"
}
```

#### Required `shop_images` Table Compatibility

| Column | Type | Nullable | Value Source | Status |
|---|---|---|---|---|
| `image_id` | `integer` | NOT NULL (PK, auto) | DB auto-increment | ✅ DB auto-fills |
| `shop_id` | `integer` (FK) | NOT NULL | URL path param | ✅ Frontend sends |
| `image_url` | `text` | NOT NULL | JSON body `image_url` | ✅ Frontend sends |
| `created_at` | `timestamp` | auto | DB default `now()` | ✅ DB auto-fills |

---

## 6. Critical `user_roles` Wiring

This is the most important part. After inserting into `clients` or `tailors`, the backend endpoint **must also** insert a row into `user_roles`. This is what drives role-based access control for every subsequent request.

```sql
-- After INSERT INTO clients (or tailors) ...

-- Step 1: Look up the numeric role_id
SELECT id FROM roles WHERE name = 'client';   -- or 'tailor'
-- Returns e.g.: 1

-- Step 2: Insert into user_roles
INSERT INTO user_roles (firebase_uid, role_id)
VALUES ('<uid_from_jwt>', 1)
ON CONFLICT DO NOTHING;
```

> **If `user_roles` is NOT populated**, the `GET /api/v1/auth/me/role` endpoint (called by the frontend `AuthContext` on every page load) will return `404`, the frontend will treat the user as unregistered, and redirect them to `/onboarding` in a loop.

---

## 7. Role Lookup Endpoint

```
GET /api/v1/auth/me/role
Authorization: Bearer <firebase_id_token>
```

#### Expected Success Response `200`

```json
{ "role": "client" }
// or
{ "role": "tailor" }
```

#### Expected Failure Response `404`

```json
{ "detail": "User role not found" }
```

The frontend `AuthContext` treats `404` as "new user, no role yet" and sends them to `/onboarding`. Any other status throws and logs an error.

> **Backend must query `user_roles` joined to `roles` to return the role name string, not the integer `role_id`.**

---

## 8. Updated Endpoint Contracts

### `GET /api/v1/profiles/client/{id}` — Response Schema

```json
{
  "id":           "string",
  "display_name": "string | null",
  "email":        "string | null",
  "photo_url":    "string | null",
  "phone":        "string | null",
  "city":         "string | null",
  "address":      "string | null",
  "created_at":   "ISO 8601 timestamp | null",
  "updated_at":   "ISO 8601 timestamp | null"
}
```

### `GET /api/v1/profiles/tailor/{id}` — Response Schema

```json
{
  "id":           "string",
  "display_name": "string | null",
  "email":        "string | null",
  "photo_url":    "string | null",
  "phone":        "string | null",
  "city":         "string | null",
  "address":      "string | null",
  "nic_front":    "string | null",
  "nic_rear":     "string | null",
  "is_verified":  "boolean",
  "created_at":   "ISO 8601 timestamp | null",
  "updated_at":   "ISO 8601 timestamp | null"
}
```

### `PATCH /api/v1/profiles/client/{id}` — New Endpoint

**Auth:** Bearer token. Verify `uid == id`.  
**Success:** `200 OK` — Partial update, only overwrite fields that are provided.

```json
{
  "phone":   "string | null",
  "city":    "string | null",
  "address": "string | null"
}
```

**Response:** Same schema as `GET /api/v1/profiles/client/{id}`.

### `PATCH /api/v1/profiles/tailor/{id}` — New Endpoint

**Auth:** Bearer token. Verify `uid == id`.  
**Success:** `200 OK` — Partial update, only overwrite fields that are provided.

```json
{
  "phone":     "string | null",
  "city":      "string | null",
  "address":   "string | null",
  "nic_front": "string | null",
  "nic_rear":  "string | null"
}
```

**Response:** Same schema as `GET /api/v1/profiles/tailor/{id}`.

### `GET /api/v1/shops/*` — All Shop Endpoints Updated

All shop list and detail endpoints must now include `specialty`. Applies to: `GET /shops/`, `GET /shops/nearby`, `GET /shops/{shop_id}`, `GET /shops/tailor/{tailor_id}`.

```json
{
  "shop_id":             "integer",
  "tailor_id":           "string",
  "shop_name":           "string",
  "specialty":           "string | null",
  "shop_bio":            "string | null",
  "shop_address":        "string | null",
  "city":                "string | null",
  "contact_number":      "string | null",
  "registration_number": "string | null",
  "latitude":            "number | null",
  "longitude":           "number | null",
  "average_rating":      "number",
  "images":              "ShopImage[]",
  "created_at":          "ISO 8601 timestamp | null",
  "updated_at":          "ISO 8601 timestamp | null"
}
```

---

## 9. Auth Middleware — No Changes Required

The Firebase ID token verification middleware is unchanged:

1. Extract `Authorization: Bearer <token>` from the request header.
2. Verify the token with the Firebase Admin SDK.
3. Decode the `uid` claim from the token payload.
4. Use `uid` as the user identifier for all DB operations — **never trust a UID sent in the request body**.

**There is no Supabase JWT involved in user auth.** Firebase tokens are the sole authentication mechanism.

---

## 10. Data Gap — JWT Claims

The entity dictionary defines `display_name`, `email`, and `photo_url` on both the `clients` and `tailors` tables. **These fields are NOT in the JSON request body.** They must be read from the decoded Firebase JWT.

| JWT Claim | Maps to DB column |
|---|---|
| `sub` | `id` (PK) |
| `name` | `display_name` |
| `email` | `email` |
| `picture` | `photo_url` |

---

## 11. NIC Image Upload — Current State (Placeholder)

> ⚠️ **Both registration forms currently use a placeholder Cloudinary URL** (`https://res.cloudinary.com/demo/image/upload/sample.jpg`) for all image uploads (profile, shop, NIC front, NIC rear). Real Cloudinary upload is implemented in the **onboarding page** only.

The `nic_front` and `nic_rear` columns in `tailors` will receive a real Cloudinary URL once `NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME` and `NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET` are configured in `.env.local`. The column type should be `text` (nullable) — no format validation beyond that.

---

## 12. What Was Removed (Frontend)

| Removed | Replaced By |
|---|---|
| Firestore `users` collection — all reads & writes | Supabase via backend API endpoints |
| `lib/firebase/user-profile.ts` (entire file deleted) | `POST /api/v1/profiles/client` and `/tailor` |
| `db` (Firestore instance) export from `config.ts` | Removed — Firebase Auth only |
| `onSnapshot` Firestore listener in `AuthContext` | `GET /api/v1/auth/me/role` on login |
| `specialty` written to Firestore `users` doc | `specialty` sent in `POST /api/v1/shops/` body |

---

## 13. Master Verification Checklist

### Database

- [ ] `clients` table: `display_name`, `email`, `photo_url`, `phone`, `city`, `address` columns added (nullable TEXT)
- [ ] `tailors` table: `display_name`, `email`, `photo_url`, `phone`, `city`, `address` columns added (nullable TEXT)
- [ ] `shops` table: `specialty` column added (nullable TEXT)
- [ ] `roles` table: contains rows `'client'`, `'tailor'` with **lowercase** names

### `POST /api/v1/profiles/client`

- [ ] Extract `firebase_uid`, `email`, `display_name`, `photo_url` from JWT claims
- [ ] Insert row into `clients` table with all columns
- [ ] Look up `role_id` from `roles` table where `name = 'client'`
- [ ] Insert row into `user_roles` (`firebase_uid`, `role_id`) — within same transaction
- [ ] Return `201` with the created client object
- [ ] Return `409` if `clients.id` already exists

### `POST /api/v1/profiles/tailor`

- [ ] Extract `firebase_uid`, `email`, `display_name`, `photo_url` from JWT claims
- [ ] Insert row into `tailors` table with all columns (set `is_verified = false`)
- [ ] Look up `role_id` from `roles` table where `name = 'tailor'`
- [ ] Insert row into `user_roles` (`firebase_uid`, `role_id`) — within same transaction
- [ ] Return `201` with the created tailor object
- [ ] Return `409` if `tailors.id` already exists

### `POST /api/v1/shops/`

- [ ] Extract `firebase_uid` from JWT → use as `tailor_id`
- [ ] Accept and store `specialty`
- [ ] Default `average_rating` to `0.0`
- [ ] Return `201` with full shop object **including `shop_id`**

### `POST /api/v1/shops/{shop_id}/images`

- [ ] Insert row into `shop_images` table
- [ ] Return `201` with the created image object

### `GET /api/v1/profiles/client/{id}`

- [ ] Returns full profile including `display_name`, `email`, `photo_url`

### `GET /api/v1/profiles/tailor/{id}`

- [ ] Returns full profile including `display_name`, `email`, `photo_url`

### `PATCH /api/v1/profiles/client/{id}`

- [ ] New endpoint created and working
- [ ] Partial update — only overwrite fields that are provided

### `PATCH /api/v1/profiles/tailor/{id}`

- [ ] New endpoint created and working
- [ ] Partial update — only overwrite fields that are provided

### `PUT /api/v1/shops/{shop_id}`

- [ ] Accepts and updates `specialty`

### `GET /api/v1/shops/*` (all shop endpoints)

- [ ] All responses include `specialty`

### `GET /api/v1/auth/me/role`

- [ ] Query `user_roles` JOIN `roles` for the authenticated `firebase_uid`
- [ ] Return `{ "role": "client" | "tailor" }` on success (`200`)
- [ ] Return `404` if no row found in `user_roles` — critical for onboarding loop prevention

---

## 14. Frontend Source File Reference

| File | Purpose |
|---|---|
| `components/auth/register-forms.tsx` | Client + Tailor registration form components |
| `lib/api/endpoints/profiles.ts` | `createClientProfile`, `createTailorProfile` |
| `lib/api/endpoints/shops.ts` | `createShop`, `addShopImage` |
| `lib/api/endpoints/auth.ts` | `getMyRole` |
| `lib/api/client.ts` | Core `apiFetch` wrapper (injects Bearer token) |
| `lib/api/types/profile.ts` | Request/response type definitions |
| `lib/api/types/shop.ts` | Shop type definitions |
| `lib/firebase/AuthContext.ts` | Role state management; calls `getMyRole` on auth state change |
| `docs/ENTITY_DICTIONARY.md` | Full DB schema reference |
