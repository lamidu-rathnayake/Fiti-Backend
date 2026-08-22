# Fiti Backend: Clean Architecture & File Structure Report

This document provides a comprehensive explanation of every file in the `app/` directory of the **Fiti Backend Application**. It details how **Clean Architecture** principles are applied and uses a **Real-World End-to-End User Scenario** to trace how data flows through every layer.

---

## 🏛️ 1. Architecture Overview & Design Principles

The application is structured into strict concentric layers according to **Clean Architecture** (Uncle Bob):

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           API LAYER (v1 endpoints)                       │
│  [profiles.py, shops.py, orders.py] ──(Uses Pydantic Schemas)           │
├─────────────────────────────────────────────────────────────────────────┤
│                        USE CASES LAYER (Application Logic)              │
│  [ManageProfileUseCase, ManageShopUseCase, ManageOrderUseCase]           │
├─────────────────────────────────────────────────────────────────────────┤
│                          DOMAIN LAYER (Pure Python)                     │
│  [Entities: Client, Tailor, Shop, Order] [Abstract Repositories]         │
├─────────────────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE LAYER (Database & External)           │
│  [SQLAlchemy Models & Repositories] [Firebase Admin SDK Security]       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Principles Applied:
1. **Dependency Inversion**: High-level business logic (Domain/Use Cases) never depends on low-level details (SQLAlchemy/FastAPI). Instead, low-level details depend on abstract interfaces defined in the domain.
2. **Framework Agnostic Domain**: The `app/domain` layer contains pure Python dataclasses without any FastAPI or SQLAlchemy imports.
3. **Decoupled Identity (Hybrid Model)**: User authentication (passwords, JWTs) is offloaded to Firebase Auth. PostgreSQL strictly manages business entity extensions using the Firebase `uid` string as primary key.

---

## 📁 2. Detailed File-by-File Breakdown

### 🟢 `app/` Root Entrypoint
- `app/main.py`: The entrypoint of the FastAPI application. Sets up CORS middleware, registers router `/api/v1`, defines global exception handlers, and manages database connection lifecycles on startup/shutdown.
- `app/__init__.py`: Package initialization.

---

### ⚙️ `app/core/` — Infrastructure Core & Configuration
- `app/core/config.py`: Manages environment variables using `pydantic-settings`. Defines database URLs (`DATABASE_URL`), API prefix (`API_V1_STR`), and Firebase settings (`FIREBASE_CREDENTIALS_PATH`, `MOCK_FIREBASE_AUTH`).
- `app/core/database.py`: Configures the async SQLAlchemy engine (`create_async_engine`) and async session maker (`async_sessionmaker`). Exposes `get_db_session()` dependency for FastAPI.
- `app/core/security.py`: Implements Option 2 Firebase authentication. Uses `HTTPBearer` and `firebase-admin` SDK to statelessly verify incoming JWT Bearer Tokens and return the authenticated `user_uid`.

---

### 🧠 `app/domain/` — The Core Business Domain (Pure Python)

#### 🔹 Entities (`app/domain/entities/`)
- `user.py`: Defines `Client`, `Tailor`, and `MeasurementProfile` domain entities.
- `shop.py`: Defines the `Shop` entity representing a tailor shop.
- `order.py`: Defines marketplace order entities: `ClothingRequest`, `ShopRequest`, `Bid`, `Order`, `Payment`, and `Rating`.
- `rbac.py`: Defines `Role`, `Permission`, and `UserRole` entities.
- `support.py`: Defines notification and support entities.

#### 🔹 Repository Contracts (`app/domain/repositories/`)
- `profile_repository.py`: Abstract Base Classes (`AbstractClientRepository`, `AbstractTailorRepository`, `AbstractMeasurementProfileRepository`) defining required database operations.
- `shop_repository.py`: Interface (`AbstractShopRepository`) for shop persistence.
- `order_repository.py`: Interface (`AbstractOrderRepository`) for clothing requests, bids, orders, payments, and ratings.
- `rbac_repository.py`: Interface (`AbstractRBACRepository`) for roles and permissions.
- `notification_repository.py`: Interface (`AbstractNotificationRepository`) for user notifications.

#### 🔹 Business Exceptions (`app/domain/exceptions/`)
- `user.py`: Domain exceptions like `ProfileAlreadyExistsError` and `ProfileNotFoundError`.
- `shop.py`: `ShopNotFoundError`.
- `order.py`: `OrderNotFoundError`, `InvalidOrderStateError`, `BidNotFoundError`.
- `rbac.py`: `RoleNotFoundError`, `PermissionDeniedError`.

---

### ⚙️ `app/use_cases/` — Application Business Workflows

#### 🔹 DTOs (`app/use_cases/dtos/`)
- `user_dto.py`: Data Transfer Objects for client/tailor registration and body measurements.
- `shop_dto.py`: DTOs for shop creation and updates.
- `order_dto.py`: DTOs for custom clothing requests, bidding, order creation, payments, and reviews.
- `rbac_dto.py`: DTOs for role assignment.

#### 🔹 Workflows
- `user/manage_profile.py`: `ManageProfileUseCase` handles client/tailor profile creation and measurement profile upserts.
- `shop/manage_shop.py`: `ManageShopUseCase` manages shop creation, tailor shop lookup, and verification toggles.
- `order/manage_order.py`: `ManageOrderUseCase` orchestrates the complete marketplace flow (request creation → shop distribution → bid submission → bid acceptance & order creation → payment → completion → rating).
- `rbac/manage_rbac.py`: `ManageRBACUseCase` assigns and verifies fine-grained permissions.

---

### 🗄️ `app/infrastructure/` — Database Models & Implementations

#### 🔹 ORM Database Models (`app/infrastructure/db/models/`)
- `user_model.py`: SQLAlchemy models (`ClientModel`, `TailorModel`, `MeasurementProfileModel`) mapping to PostgreSQL `clients`, `tailors`, and `measurement_profile` tables.
- `shop_model.py`: `ShopModel` mapping to `shops` table.
- `order_model.py`: SQLAlchemy models (`ClothingRequestModel`, `ShopRequestModel`, `BidModel`, `OrderModel`, `PaymentModel`, `RatingModel`).
- `rbac_model.py`: `RoleModel`, `PermissionModel`, `UserRoleModel`.
- `support_model.py`: `NotificationModel`.

#### 🔹 Repository Implementations (`app/infrastructure/db/repositories/`)
- `sqlalchemy_profile_repository.py`: Concrete SQLAlchemy implementation of client, tailor, and measurement repositories.
- `sqlalchemy_shop_repository.py`: Concrete implementation for shop queries.
- `sqlalchemy_order_repository.py`: Concrete implementation handling complex relational queries and status updates for orders.
- `sqlalchemy_rbac_repository.py`: Concrete implementation for role assignments.
- `sqlalchemy_support_repository.py`: Concrete implementation for notifications.

---

### 🌐 `app/api/` — FastAPI Delivery Layer

#### 🔹 Request / Response Schemas (`app/api/schemas/`)
- `user_schema.py`: Pydantic validation schemas (`ClientRegisterRequest`, `TailorRegisterRequest`, `MeasurementProfileRequest`, etc.).
- `shop_schema.py`: `ShopCreateRequest`, `ShopResponse`.
- `order_schema.py`: `ClothingRequestCreate`, `BidSubmitRequest`, `AcceptBidRequest`, `MockPaymentRequest`, `RatingCreateRequest`.

#### 🔹 HTTP Endpoints (`app/api/v1/endpoints/`)
- `profiles.py`: Routes for client/tailor profile onboarding and body measurements (`/profiles/client`, `/profiles/tailor`).
- `shops.py`: Routes for tailor shop creation and search (`/shops/`).
- `orders.py`: Routes for marketplace interactions (`/orders/requests`, `/orders/bids`, `/orders/accept-bid`, `/orders/payments/mock`, `/orders/ratings`).
- `health.py`: Liveness check endpoint (`/health`).

#### 🔹 Wiring & Routing
- `app/api/v1/router.py`: Aggregates endpoints into the `/api/v1` router.
- `app/api/dependencies.py`: FastAPI Dependency Container. Wires Async Database Sessions → SQLAlchemy Repositories → Use Cases → HTTP Endpoints.

---

## 🎬 3. Real-World Scenario: Trace of a Complete Marketplace Flow

Let's walk through how data moves through these exact files during a complete transaction on **Fiti**.

### Scenario Narrative:
1. **User Sign-up**: Tailor *"Kamal"* signs up using Firebase Web Auth on the frontend (`uid = "tailor_kamal_123"`).
2. **Tailor Onboarding**: Web app calls `POST /api/v1/profiles/tailor`.
3. **Shop Creation**: Tailor Kamal creates *"Kamal Royal Tailors"* via `POST /api/v1/shops/`.
4. **Client Request**: Client *"Nimal"* requests a custom 3-piece suit with voice note instructions via `POST /api/v1/orders/requests`.
5. **Tailor Bidding**: Kamal submits a bid of LKR 25,000 via `POST /api/v1/orders/bids`.
6. **Order Acceptance**: Nimal accepts the bid (`POST /api/v1/orders/accept-bid`).

---

### Step-by-Step Data Flow Execution Chain:

```
[ HTTP Request ] 
       │
       ▼
1. app/api/v1/endpoints/orders.py ──(Validates JSON with Pydantic)──> app/api/schemas/order_schema.py
       │
       ├─(Extracts Auth Token)──> app/core/security.py (Firebase verify_id_token)
       ├─(Injects Dependencies)─> app/api/dependencies.py
       │
       ▼
2. app/use_cases/order/manage_order.py (ManageOrderUseCase)
       │
       ├─(Converts Schema to DTO)──> app/use_cases/dtos/order_dto.py
       ├─(Applies Business Rules & Domain Entities)──> app/domain/entities/order.py
       │
       ▼
3. app/domain/repositories/order_repository.py (Abstract Interface Call)
       │
       ▼
4. app/infrastructure/db/repositories/sqlalchemy_order_repository.py (SQLAlchemy Async Query)
       │
       ├─(Maps Domain Entity to ORM Model)──> app/infrastructure/db/models/order_model.py
       ├─(Executes Query via Session)──────> app/core/database.py (PostgreSQL DB)
       │
       ▼
[ HTTP 201 Created JSON Response Returned to Web Frontend ]
```

---

## 🎯 Summary of Architecture Benefits

1. **Testability**: Every use case can be unit-tested in complete isolation without running a real database or FastAPI server by mocking the domain repository interfaces (`AbstractOrderRepository`, etc.).
2. **Security**: Firebase handles authentication identity, while backend endpoints statelessly verify tokens via `app/core/security.py`.
3. **Flexibility**: Switching from PostgreSQL to another database or adding Redis caching only requires writing a new implementation in `app/infrastructure/db/repositories/` without touching a single line of business logic in `app/use_cases/` or `app/domain/`.
