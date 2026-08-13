# Fiti Admin Backend - Architecture & Development Plan

## 1. Overview
As per our architectural discussions, the Fiti ecosystem is being split into a **Two-Backend Architecture**:
1. **Tailor & Client Backend (Current Repository)**: Handles the core marketplace domain—shops, profiles, orders, bids, measurements, and ratings.
2. **Admin Backend (Future Repository)**: A dedicated backend solely responsible for administrative operations, system configurations, and moderation.

Currently, the Frontend is unified (housing Client, Tailor, and Admin UI components), but they will eventually be decoupled. For now, the Unified Frontend will intelligently route requests to the correct backend depending on the user's role.

## 2. Why a Separate Admin Backend?
- **Security**: Administrative endpoints (e.g., verifying a Tailor's NIC, banning users, viewing system-wide financial metrics) are isolated from the public-facing Tailor/Client API.
- **Scalability**: Administrative operations (like generating heavy reports or running background moderation tasks) will not bottleneck the consumer marketplace.
- **Maintainability**: The Tailor/Client backend remains lean and entirely focused on business logic for the marketplace.

## 3. Integration Points

### 3.1. Database Sharing vs. API Communication
The Admin Backend will need to interact with the Tailor/Client data. There are two common approaches:
* **Option A (Shared Database)**: The Admin backend connects directly to the same PostgreSQL database used by this Tailor/Client backend. This is the fastest way to build the Admin dashboard.
* **Option B (API Gateway / Microservices)**: The Admin backend communicates with the Tailor/Client backend via secure internal HTTP requests.

*Recommendation for Fiti*: **Option A** is highly recommended for this stage of the startup. It avoids complex data synchronization and keeps infrastructure simple.

### 3.2. Authentication & Redirection
The current Tailor/Client backend already natively supports this split.
In `app/api/v1/endpoints/auth.py`, when a user logs in, the `GET /api/v1/auth/me/role` endpoint evaluates their role:
```python
    if "admin" in roles:
        # Redirects the frontend to rely on the ADMIN_BACKEND_URL
        redirect_to = f"{settings.ADMIN_BACKEND_URL}/dashboard" ...
```
This ensures that Admin users are immediately handed off to the Admin space.

## 4. Planned Admin Backend Features
When we initialize the next repository for the Admin Backend, we will build the following core modules:

### 4.1. Tailor Verification & Moderation
- `GET /admin/tailors/pending`: List tailors awaiting NIC verification.
- `POST /admin/tailors/{id}/verify`: Approve a tailor's account (grants them active marketplace access).
- `POST /admin/tailors/{id}/suspend`: Temporarily hide a shop from the marketplace.

### 4.2. User Management
- `GET /admin/users`: List all registered clients and tailors.
- `POST /admin/users/roles`: Modify RBAC (Role-Based Access Control) permissions.

### 4.3. Platform Analytics & Finances
- `GET /admin/analytics/orders`: View platform-wide order volume, completion rates, and average bid prices.
- `GET /admin/analytics/revenue`: Track payments and calculate platform commission cuts.

### 4.4. Content & Taxonomy Management
- `POST /admin/categories`: Add new clothing categories to the system.

## 5. Next Steps for Implementation
1. **Initialize a new FastAPI repository** (e.g., `Fiti-Admin-Backend`).
2. **Copy the Database Models**: Replicate the SQLAlchemy models (or create a shared internal python package) so the Admin backend can read the same tables.
3. **Set up Firebase Admin SDK**: Ensure the Admin backend can read the same Firebase Authentication tokens.
4. **Build the Endpoints**: Start with the `Tailor Verification` API, as it is the most critical missing piece for the marketplace lifecycle.
