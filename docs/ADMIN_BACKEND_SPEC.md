# Fiti Admin Backend Specification

## Overview
The Fiti platform uses a microservices-style approach where the **Admin Backend** is a completely separate project from the main Fiti Backend (Client/Tailor API).

The main Fiti Backend acts as the **post-login gateway**. When an admin user signs in through the unified frontend and queries `/api/v1/auth/me/role` on the main backend, it responds with a redirect command pointing to the Admin Backend URL.

From that point forward, the admin interacts exclusively with the Admin Backend.

## Authentication Architecture
1. **Firebase Authentication**: The Admin Backend must verify Firebase ID tokens independently. It should initialize its own `firebase-admin` SDK instance.
2. **Authorization (RBAC)**: The Admin Backend must independently verify that the authenticated user possesses the `admin` role. It will need read access to the shared PostgreSQL database (specifically the `user_roles` and `roles` tables) to enforce this, or rely on Firebase Custom Claims if implemented.

## Tech Stack Recommendation
Since the Fiti Backend uses modern Python tools, the Admin Backend should ideally follow the same tech stack to allow for code sharing (e.g., sharing the domain models or database schemas as a submodule or internal package):
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (Async)
- **Validation**: Pydantic V2

## Required Capabilities
The Admin Backend should implement endpoints to manage the platform, which may include:
- **User Management**: Viewing all clients and tailors, banning/suspending users, approving tailor verification requests (reviewing NIC images).
- **Dispute Resolution**: Viewing and resolving flagged orders or shop requests.
- **System Configuration**: Managing global platform settings, service fees, or allowed clothing categories.
- **RBAC Management**: Assigning internal roles (e.g., Super Admin, Support Agent).

## Database Access
The Admin Backend will share the same PostgreSQL database as the main Fiti Backend. It should use the same schema.

**Important Considerations**:
- Avoid writing to tables that are strictly managed by the main backend unless necessary (e.g., resolving a dispute might require updating an order status).
- Adhere to the same `updated_at` trigger patterns used in the main schema.

## Integration Point
The only integration point between the main backend and the Admin Backend is the redirect URL configured in the main backend's `.env` file:
```
ADMIN_BACKEND_URL=https://admin.fiti.com
```

The unified frontend uses this URL to navigate the user to the admin console upon a successful admin login.
