# FastAPI Backend Application with Clean Architecture & SQLAlchemy

Production-ready backend application built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, and **Clean Architecture** principles.

---

## 🏛️ Clean Architecture Layers

This project follows Uncle Bob's **Clean Architecture** guidelines, maintaining strict separation of concerns and dependency rules (dependencies point inward).

```
                      +-----------------------------------+
                      |      Presentation / API Layer     |
                      |   (FastAPI Routers, Schemas, DI)  |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------+-----------------+
                      |     Application / Use Cases       |
                      |   (Services, DTOs, Workflows)     |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------+-----------------+
                      |       Domain Layer (Core)         |
                      | (Entities, Exceptions, Interfaces)|
                      +-----------------+-----------------+
                                        ^
                                        |
                      +-----------------+-----------------+
                      |       Infrastructure Layer        |
                      | (SQLAlchemy Models & Repos, DB)   |
                      +-----------------------------------+
```

### Layer Breakdown

1. **Domain Layer (`app/domain/`)**
   - **Pure Python core business logic**. Zero dependencies on FastAPI, SQLAlchemy, or external libraries.
   - `entities/`: Dataclasses representing core business objects (e.g., `User`).
   - `exceptions/`: Domain-specific exceptions (`UserNotFoundError`, `UserAlreadyExistsError`).
   - `repositories/`: Abstract repository interfaces (`AbstractUserRepository`).

2. **Use Cases / Application Layer (`app/use_cases/`)**
   - Implements application-specific business rules and operations.
   - `dtos/`: Input/Output Data Transfer Objects.
   - `user/`: Use case implementations (`CreateUserUseCase`, `GetUserUseCase`, `ListUsersUseCase`).

3. **Infrastructure Layer (`app/infrastructure/`)**
   - Contains details about external tools, frameworks, databases, and third-party libraries.
   - `db/models/`: SQLAlchemy 2.0 ORM Mapped Classes (`UserModel`) with domain mapping.
   - `db/repositories/`: Concrete implementations of domain repository interfaces using SQLAlchemy `AsyncSession`.
   - `security/`: Password hashing and authentication mechanisms.

4. **Presentation / API Layer (`app/api/`)**
   - Handles HTTP endpoints and validation.
   - `schemas/`: Pydantic V2 Request & Response models.
   - `dependencies.py`: Dependency injection container using FastAPI `Depends` to wire abstractions to concrete implementations.
   - `v1/endpoints/`: REST API controllers (`health.py`, `users.py`).

5. **Core Configuration & Entrypoint (`app/core/`, `app/main.py`)**
   - `core/config.py`: Environment settings management using `pydantic-settings`.
   - `core/database.py`: Async engine and session factory configuration.
   - `main.py`: Application entry point and lifespan event handlers.

---

## 📁 Directory Structure

```
.
├── app/
│   ├── api/                    # Presentation Layer (HTTP / REST)
│   │   ├── dependencies.py     # FastAPI Dependency Injection Container
│   │   ├── schemas/            # Pydantic Request/Response Models
│   │   │   └── user_schema.py
│   │   └── v1/
│   │       ├── router.py       # Central API v1 Router
│   │       └── endpoints/
│   │           ├── health.py
│   │           └── users.py
│   ├── core/                   # Core Infrastructure & Configuration
│   │   ├── config.py           # App Settings (Pydantic BaseSettings)
│   │   └── database.py         # Async SQLAlchemy Engine & Session setup
│   ├── domain/                 # Domain Layer (Enterprise Rules)
│   │   ├── entities/           # Pure Domain Entities
│   │   │   └── user.py
│   │   ├── exceptions/         # Domain Exceptions
│   │   │   └── user.py
│   │   └── repositories/       # Abstract Repository Contracts
│   │       └── user_repository.py
│   ├── infrastructure/         # Infrastructure Layer (Data & Framework Adapters)
│   │   ├── db/
│   │   │   ├── base.py         # SQLAlchemy Base
│   │   │   ├── models/         # SQLAlchemy ORM Models
│   │   │   │   └── user_model.py
│   │   │   └── repositories/   # SQLAlchemy Repository Implementations
│   │   │       └── sqlalchemy_user_repository.py
│   │   └── security/           # Hashing & Auth utilities
│   │       └── hashing.py
│   ├── use_cases/              # Application Layer (Use Cases)
│   │   ├── dtos/               # Application DTOs
│   │   │   └── user_dto.py
│   │   └── user/               # User Use Cases
│   │       ├── create_user.py
│   │       ├── get_user.py
│   │       └── list_users.py
│   └── main.py                 # Application Lifespan & FastAPI Factory
├── .env                        # Environment variables
├── pyproject.toml              # Project dependencies
└── main.py                     # Entrypoint script
```

---

## 🚀 Getting Started

### 1. Install Dependencies
Using `uv`:
```bash
uv sync
```
Or using standard `pip`:
```bash
pip install -e .
```

### 2. Run the Application
```bash
uv run python main.py
```
Or using uvicorn directly:
```bash
uv run uvicorn app.main:app --reload
```

### 3. API Documentation
Once running, open your browser at:
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
