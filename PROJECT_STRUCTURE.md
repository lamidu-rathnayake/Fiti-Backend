# Fiti Microservice - Project Structure

This project is a **FastAPI Microservice** built with **Clean Architecture** (Domain-Driven Design / Layered Architecture) principles using **SQLAlchemy 2.0 (Async)** and **Pydantic V2**.

---

## 📂 Top-Level Overview

```
.
├── app/                  # Main application package containing clean architecture layers
├── tests/                # Automated tests (API & Use case test suites)
├── main.py               # Root execution entrypoint script
├── pyproject.toml        # Project metadata, dependencies (uv/pip), and pytest config
└── README.md             # Project documentation
```

---

## 🏛️ Clean Architecture Breakdown (`app/`)

Dependencies flow **inward**: Presentation → Use Cases → Domain ← Infrastructure.

```
                      +-----------------------------------+
                      |   1. Presentation / API Layer     |
                      |    (app/api - FastAPI, Schemas)   |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------+-----------------+
                      |   2. Application / Use Cases      |
                      |   (app/use_cases - Logic, DTOs)   |
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

### 1. Domain Layer (`app/domain/`) — *Enterprise Core*
Contains pure Python business logic and domain definitions. It has **zero dependencies** on external frameworks or databases.
* **Entities** (`app/domain/entities/user.py`): Pure dataclasses representing core business objects.
* **Exceptions** (`app/domain/exceptions/user.py`): Domain-specific error types (e.g., `UserNotFoundError`, `UserAlreadyExistsError`).
* **Repositories** (`app/domain/repositories/user_repository.py`): Abstract base class contracts (`AbstractUserRepository`) specifying database interaction interfaces.

### 2. Application / Use Cases Layer (`app/use_cases/`) — *Application Logic*
Coordinates data flow to and from domain entities, orchestrating specific operations.
* **DTOs** (`app/use_cases/dtos/user_dto.py`): Data Transfer Objects for input and output data structures.
* **User Operations** (`app/use_cases/user/`):
  * `create_user.py`: Handles user registration logic.
  * `get_user.py`: Retrieves a single user by ID.
  * `list_users.py`: Fetches paginated user lists.

### 3. Infrastructure Layer (`app/infrastructure/`) — *Framework & Database Adapters*
Handles low-level technical details and implements interfaces defined in the domain layer.
* **Database Models** (`app/infrastructure/db/models/user_model.py`): SQLAlchemy 2.0 ORM Mapped models (`UserModel`).
* **Repositories** (`app/infrastructure/db/repositories/sqlalchemy_user_repository.py`): Concrete SQLAlchemy implementation of `AbstractUserRepository`.
* **Security** (`app/infrastructure/security/hashing.py`): Password hashing and verification utilities.

### 4. Presentation / API Layer (`app/api/`) — *HTTP & REST Controller*
Exposes endpoints, validates incoming JSON payloads, and handles HTTP responses.
* **Dependencies** (`app/api/dependencies.py`): Dependency injection wiring using FastAPI `Depends` to inject repository and use-case instances.
* **Schemas** (`app/api/schemas/user_schema.py`): Pydantic V2 Request and Response models.
* **Endpoints** (`app/api/v1/endpoints/`): HTTP route definitions (`users.py` and `health.py`).

### 5. Configuration & App Lifecycle (`app/core/` & `app/main.py`)
* **Config** (`app/core/config.py`): Environment settings using `pydantic-settings`.
* **Database** (`app/core/database.py`): Async engine and session sessionmaker setup.
* **App Factory** (`app/main.py`): FastAPI app initialization and lifespan database table creation.

---

## 🧪 Test Suite (`tests/`)

* `tests/test_api.py`: Integration tests verifying HTTP endpoints using `httpx.AsyncClient`.
* `tests/test_use_cases.py`: Unit tests for use case business logic.
