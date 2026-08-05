# Fiti Backend Application - Project Structure & Clean Architecture Guide

This project is a **FastAPI Application** built with **Clean Architecture** (Domain-Driven Design / Layered Architecture) principles using **SQLAlchemy 2.0 (Async)**, **PostgreSQL**, and **Pydantic V2**.

---

## 📂 Top-Level Overview

```
.
├── app/                  # Main application package containing clean architecture layers
├── tests/                # Automated tests (API & Use case test suites)
├── main.py               # Root execution entrypoint script
├── schema.sql            # Raw PostgreSQL DDL for production DB migrations & seeding
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

## 📁 Detailed Directory & Component Breakdown

### 1. Domain Layer (`app/domain/`) — *Enterprise Core*
Contains pure Python business logic, dataclasses, and domain interfaces. It has **zero dependencies** on external frameworks, FastAPI, or SQLAlchemy.

* **Entities (`app/domain/entities/`)**: Pure dataclasses representing core domain objects.
  * `user.py`: `User`, `MeasurementProfile`, `Client`, `Seller`, `GenderEnum`.
  * `shop.py`: `Shop`, `ShopImage`.
  * `order.py`: `ClothingRequest`, `ClothingRequestImage`, `Measurement`, `ShopRequest`, `Bid`, `Order`, `Payment`, `Rating`, `FabricStatusEnum`, `ServiceTypeEnum`, `ClothingRequestStatusEnum`, `ShopRequestStatusEnum`, `OrderStatusEnum`, `PaymentMethodEnum`, `PaymentStatusEnum`.
  * `rbac.py`: `Role`, `UserRole`, `Section`, `RoleSectionGrant`, `SubSection`, `SectionSubSection`.
  * `support.py`: `Notification`, `FavoriteShop`.

* **Exceptions (`app/domain/exceptions/`)**: Custom domain exception hierarchy.
  * `user.py`: `UserNotFoundError`, `UserAlreadyExistsError`, `InvalidUserDataError`.
  * `shop.py`: `ShopNotFoundError`, `ShopAlreadyExistsError`.
  * `order.py`: `OrderNotFoundError`, `ClothingRequestNotFoundError`, `ShopRequestNotFoundError`, `InvalidOrderStateTransitionError`.
  * `rbac.py`: `RoleNotFoundError`, `SectionNotFoundError`, `UnauthorizedSectionAccessError`.

* **Repositories (`app/domain/repositories/`)**: Abstract Base Classes defining persistence contracts.
  * `user_repository.py`: `AbstractUserRepository`.
  * `shop_repository.py`: `AbstractShopRepository`.
  * `order_repository.py`: `AbstractOrderRepository`.
  * `rbac_repository.py`: `AbstractRBACRepository`.
  * `notification_repository.py`: `AbstractNotificationRepository`.

---

### 2. Application / Use Cases Layer (`app/use_cases/`) — *Business Workflows*
Orchestrates domain entities to execute application use cases.

* **Data Transfer Objects (`app/use_cases/dtos/`)**:
  * `user_dto.py`: DTOs for user creation, measurements, seller registration, and user profiles.
  * `shop_dto.py`: DTOs for shop registration, updates, search, and images.
  * `order_dto.py`: DTOs for clothing requests (voice notes, design images, service toggles), bids, orders, mock payments, and ratings.
  * `rbac_dto.py`: DTOs for roles, route access grants, and sub-sections.
  * `support_dto.py`: DTOs for notifications and favorite shops.

* **Workflows (`app/use_cases/`)**:
  * `user/`: `manage_profile.py` (client and seller registration).
  * `shop/`: `manage_shop.py` (create, update, fetch, search near location).
  * `order/`: `manage_order.py` (create requests, submit bids, accept bids, transition order states, process payments, submit ratings).
  * `rbac/`: `manage_rbac.py` (manage roles, sections, user role assignments).
  * `support/`: `manage_support.py` (manage notifications, favorite shops).

---

### 3. Infrastructure Layer (`app/infrastructure/`) — *Framework & Database Adapters*
Handles technical details, external services, and SQLAlchemy 2.0 ORM persistent storage.

* **Database Models (`app/infrastructure/db/models/`)**:
  * `user_model.py`: SQLAlchemy mapped models for `users`, `measurement_profile`, `clients`, `sellers`.
  * `shop_model.py`: Mapped models for `shops`, `shop_images`, `favorite_shops`.
  * `order_model.py`: Mapped models for `clothing_requests`, `clothing_request_images`, `measurements`, `shop_requests`, `bids`, `orders`, `payments`, `ratings`.
  * `rbac_model.py`: Mapped models for `roles`, `user_roles`, `sections`, `role_section_grants`, `sub_sections`, `section_sub_sections`.
  * `support_model.py`: Mapped models for `notifications`.

* **Repositories (`app/infrastructure/db/repositories/`)**:
  * `sqlalchemy_user_repository.py`
  * `sqlalchemy_shop_repository.py`
  * `sqlalchemy_order_repository.py`
  * `sqlalchemy_rbac_repository.py`
  * `sqlalchemy_support_repository.py`

* **Security (`app/infrastructure/security/`)**:
  * `hashing.py`: Password hashing/verification logic.

---

### 4. Presentation / API Layer (`app/api/`) — *HTTP & REST Controllers*

* **Dependencies (`app/api/dependencies.py`)**: Dependency injection factory for database sessions, repositories, and use case services.
* **Schemas (`app/api/schemas/`)**: Pydantic V2 request & response validation models (`user_schema.py`, `shop_schema.py`, `order_schema.py`).
* **Endpoints (`app/api/v1/endpoints/`)**:
  * `health.py`: Application health check endpoint (`/api/v1/health`).
  * `profiles.py`: Client and seller registration/profiles (`/api/v1/profiles`).
  * `shops.py`: Tailor shop registration, updates, and geospatial discovery (`/api/v1/shops`).
  * `orders.py`: Clothing requests, bids, orders, mock payments, ratings (`/api/v1/orders`).
  * `rbac.py`: Role assignments and route access verification (`/api/v1/rbac`).
  * `support.py`: Notifications and favorite shops (`/api/v1/support`).
* **Router (`app/api/v1/router.py`)**: Central API router combining all v1 endpoints under `/api/v1`.

---

### 5. Configuration & Lifespan (`app/core/` & `app/main.py`)
* `app/core/config.py`: Environment configuration via `pydantic-settings`.
* `app/core/database.py`: SQLAlchemy async engine (`create_async_engine`) and session sessionmaker.
* `app/main.py`: FastAPI app initialization, CORS middleware, API router inclusion, and lifespan DB schema creation.

---

## 🧪 Test Suite (`tests/`)

* `tests/test_api.py`: Async HTTP integration tests verifying end-to-end marketplace flows (Client/Seller creation -> Shop setup -> Request creation with voice notes & design images -> Bidding -> Order completion -> Mock payment -> Rating).
* `tests/test_use_cases.py`: Unit tests for domain logic and use case exception handling.

---

## 🛠️ Code Quality & Typing

This project strictly adheres to modern Python standards:
* **Python 3.12+ Typing**: Uses built-in `list` and union operators `| None` in place of legacy `typing` constructs (`List`, `Optional`).
* **Static Analysis**: Enforced by `mypy` for strict type checking across the entire domain, use cases, and infrastructure.
* **Linting & Formatting**: Maintained by `ruff` for consistent style and auto-fixing of syntax conventions.
