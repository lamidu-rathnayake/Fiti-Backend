# Fiti Backend Application - Project Structure & Clean Architecture Guide

This project is a **FastAPI Application** built with **Clean Architecture** (Domain-Driven Design / Layered Architecture) principles using **Firebase Auth & Firestore DB** for Identity/Roles, **SQLAlchemy 2.0 (Async)**, **PostgreSQL** for Business Domain Storage (Shops, Orders, Bids, Measurements), and **Pydantic V2**.

---

## 📂 Top-Level Overview

```
.
├── app/                  # Main application package containing clean architecture layers
├── fiti-front/           # Next.js frontend web application (Firebase Auth & Firestore DB client)
├── tests/                # Automated tests (API & Use case test suites)
├── main.py               # Root execution entrypoint script
├── Dev-Manual/           # Architecture reports and API documentation
├── schema.sql            # Raw PostgreSQL DDL for domain data tables
├── pyproject.toml        # Project metadata, dependencies (uv/pip), and pytest config
└── PROJECT_STRUCTURE.md  # Clean Architecture documentation & directory layout
```

---

## 🏛️ Clean Architecture Breakdown (`app/`)

Dependencies strictly flow **inward**: Presentation → Use Cases → Domain ← Infrastructure.

```
                      +-----------------------------------+
                      |   1. Presentation / API Layer     |
                      |   (app/api - FastAPI, Schemas)    |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------+-----------------+
                      |   2. Application / Use Cases      |
                      |  (app/use_cases - Logic, DTOs)    |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------+-----------------+
                      |     3. Domain Layer (Core)        |
                      |  (app/domain - Entities, Rules)   |
                      +-----------------+-----------------+
                                        ^
                                        |
                      +-----------------+-----------------+
                      |    4. Infrastructure Layer        |
                      |  (app/infrastructure - DB, ORM)   |
                      +-----------------------------------+
```

---

## 🔐 Post-Login Architecture & Role Enforcement

Fiti utilizes a **Firebase-Native Identity Architecture**:

1. **Firebase Authentication & Firestore DB**:
   - All users authenticate via Google SSO or Email/Password directly on the web application.
   - User profiles and role assignments (`client`, `seller`) are stored in the Firestore `users` collection (`users/{uid}`).
   - PostgreSQL contains zero user/role tables.

2. **Gateway Endpoint (`GET /api/v1/auth/me/role`)**:
   - Accepts the Firebase Bearer token, verifies token validity, checks the user's role from JWT claims or Firestore DB, and returns the appropriate client (`/client/home`) or seller (`/seller/dashboard`) route.

3. **Role Enforcement (`require_role`)**:
   - Protected endpoints are guarded by the `require_role("role_name")` dependency in `app/core/security.py`.
   - Token payload claims are checked first; if un-claimed, role authorization is verified against the Firestore `users` collection (`firebase_admin.firestore`).

---

## 📁 Detailed Directory & Component Breakdown

### 1. Domain Layer (`app/domain/`) — *Enterprise Core*
Contains pure Python business logic, dataclasses, and domain interfaces.

* **Entities (`app/domain/entities/`)**: Pure dataclasses representing core domain objects.
  * `user.py`: `MeasurementProfile`, `Client`, `Tailor`, `GenderEnum`.
  * `shop.py`: `Shop`, `ShopImage`.
  * `order.py`: `ClothingRequest`, `ClothingRequestImage`, `Measurement`, `ShopRequest`, `Bid`, `Order`, `Payment`, `Rating`, `FabricStatusEnum`, `ServiceTypeEnum`, `ClothingRequestStatusEnum`, `ShopRequestStatusEnum`, `OrderStatusEnum`, `PaymentMethodEnum`, `PaymentStatusEnum`.
  * `support.py`: `Notification`, `FavoriteShop`.

* **Repositories (`app/domain/repositories/`)**: Abstract Base Classes defining persistence contracts.
  * `profile_repository.py`: `AbstractClientRepository`, `AbstractTailorRepository`, `AbstractMeasurementProfileRepository`.
  * `shop_repository.py`: `AbstractShopRepository`.
  * `order_repository.py`: `AbstractOrderRepository`.
  * `support_repository.py`: `AbstractSupportRepository`.

---

### 2. Application / Use Cases Layer (`app/use_cases/`) — *Business Workflows*
Orchestrates domain entities to execute application use cases.

* **Workflows (`app/use_cases/`)**:
  * `user/`: `manage_profile.py` (measurements, profile retrieval).
  * `shop/`: `manage_shop.py` (create, update, fetch, search near location).
  * `order/`: `manage_order.py` (create requests, cancel requests, submit bids, accept bids, transition order states, process payments, submit ratings).
  * `support/`: `manage_support.py` (manage notifications, favorite shops).

---

### 3. Infrastructure Layer (`app/infrastructure/`) — *Framework & Database Adapters*
Handles technical details, external services, and SQLAlchemy 2.0 ORM persistent storage.

* **Database Models (`app/infrastructure/db/models/`)**:
  * `user_model.py`: Mapped models for `measurement_profile`, `clients`, `tailors` (referenced by Firebase UID).
  * `shop_model.py`: Mapped models for `shops`, `shop_images`.
  * `order_model.py`: Mapped models for `clothing_requests`, `clothing_request_images`, `measurements`, `shop_requests`, `bids`, `orders`, `payments`, `ratings`.
  * `support_model.py`: Mapped models for `notifications`, `favorite_shops`.

---

### 4. Presentation / API Layer (`app/api/`) — *HTTP & REST Controllers*

* **Endpoints (`app/api/v1/endpoints/`)**:
  * `auth.py`: Post-login gateway (`/api/v1/auth/me/role`).
  * `health.py`: Application health check endpoint (`/api/v1/health`).
  * `profiles.py`: Client and tailor profiles/measurements (`/api/v1/profiles`).
  * `shops.py`: Tailor shop registration, updates, and geospatial discovery (`/api/v1/shops`).
  * `orders.py`: Clothing requests, bids, orders, mock payments, ratings (`/api/v1/orders`).
  * `support.py`: Notifications and favorite shops (`/api/v1/support`).
* **Router (`app/api/v1/router.py`)**: Central API router combining all v1 endpoints under `/api/v1`.

---

### 5. Configuration & Security (`app/core/` & `app/main.py`)
* `app/core/config.py`: Environment configuration via `pydantic-settings`.
* `app/core/database.py`: SQLAlchemy async engine (`create_async_engine`) and session factory.
* `app/core/security.py`: Firebase token verification (`get_current_user`, `get_current_user_uid`) and Firestore DB `require_role` guard factory.
* `app/main.py`: FastAPI app initialization, CORS middleware, API router inclusion.
