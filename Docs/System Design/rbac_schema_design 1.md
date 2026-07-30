# Hybrid Architecture & Role-Based Access Control (RBAC) Schema Design

This document outlines the architecture and database schema design for system authentication, user profile storage, and fine-grained Role-Based Access Control (RBAC).

---

## 1. System Architecture Overview

The system uses a **Hybrid Cloud Architecture** separating Authentication, Document/Profile storage, and Relational RBAC logic:

```
┌─────────────────────────────────┐       ┌─────────────────────────┐       ┌─────────────────────────┐
│          Firebase Auth          │       │        Firestore        │       │       PostgreSQL        │
├─────────────────────────────────┤       ├─────────────────────────┤       ├─────────────────────────┤
│ • Google Sign-In (OAuth)        │       │ • User Login Profiles   │       │ • Relational Business   │
│ • Email / Password Auth         │ ───►  │ • Real-time Metadata    │ ───►  │   Logic & Domain Data   │
│ • Password Hashing (Internal)   │ (UID) │ • Preferences & State   │ (UID) │ • Fine-grained RBAC     │
│ • JWT Tokens, Sessions & Claims │       │ • Synced User Docs      │       │   (Sections & Grants)   │
└─────────────────────────────────┘       └─────────────────────────┘       └─────────────────────────┘
```

1. **Firebase Auth:** Handles identity verification supporting both **Google Sign-In (OAuth)** and **Email / Password** login. Manages password hashing internally, issues JWT tokens, and sets Custom User Claims (e.g., `{ "role": "seller" }`).
2. **Firestore:** Serves as the primary store for user profile documents, real-time user status, and flexible metadata indexed by the Firebase `uid`.
3. **PostgreSQL:** Stores structured domain entities and relational RBAC mappings (roles, sections, sub-sections, and grants), referencing users via their Firebase `uid` (`VARCHAR(128)`).

---

## 2. PostgreSQL Relational Database Schema

### 2.1 `users` Table

Stores application-level user records linked to Firebase Auth using `firebase_uid`.

| Column Name     | Data Type    | Constraints       | Description                                                  |
| :-------------- | :----------- | :---------------- | :----------------------------------------------------------- |
| `id`            | VARCHAR(128) | PK                | Unique Firebase Auth UID.                                    |
| `name`          | VARCHAR(150) | NOT NULL          | User's full name.                                            |
| `age`           | INT          | CHECK (`age` >= 0)| User's age.                                                  |
| `email`         | VARCHAR(255) | UNIQUE, NOT NULL  | Primary email address (synced with Firebase Auth).            |
| `auth_provider` | VARCHAR(50)  | NOT NULL          | Authentication provider (e.g., `google.com`, `password`).    |
| `is_active`     | BOOLEAN      | DEFAULT TRUE      | Soft-disable account access without deleting relational data.|
| `created_at`    | TIMESTAMP    | DEFAULT NOW()     | Account creation timestamp.                                  |
| `updated_at`    | TIMESTAMP    | DEFAULT NOW()     | Profile last updated timestamp.                              |

---

### 2.2 `sellers` Table

Stores specific seller profile attributes and verification details, linked to Firebase Auth via `id`.

| Column Name     | Data Type    | Constraints       | Description                                                  |
| :-------------- | :----------- | :---------------- | :----------------------------------------------------------- |
| `id`            | VARCHAR(128) | PK, FK `users(id)`| Unique Firebase Auth UID referencing `users(id)`.            |
| `name`          | VARCHAR(150) | NOT NULL          | Seller/Business name.                                        |
| `age`           | INT          | CHECK (`age` >= 0)| Seller owner age.                                            |
| `email`         | VARCHAR(255) | UNIQUE, NOT NULL  | Seller email address.                                        |
| `auth_provider` | VARCHAR(50)  | NOT NULL          | Authentication provider (e.g., `google.com`, `password`).    |
| `nic_front`     | VARCHAR(500) | NULLABLE          | Storage URL/Path for NIC front image verification.           |
| `nic_rear`      | VARCHAR(500) | NULLABLE          | Storage URL/Path for NIC rear image verification.            |
| `is_active`     | BOOLEAN      | DEFAULT TRUE      | Seller account status.                                       |
| `created_at`    | TIMESTAMP    | DEFAULT NOW()     | Account creation timestamp.                                  |
| `updated_at`    | TIMESTAMP    | DEFAULT NOW()     | Profile last updated timestamp.                              |

---

### 2.3 `roles` Table

Defines available system roles (`User`, `Seller`, `Admin`, `Tailor`).

| Column Name | Data Type   | Constraints        | Description                                    |
| :---------- | :---------- | :----------------- | :--------------------------------------------- |
| `id`        | INT         | PK, Auto Increment | Unique role identifier.                        |
| `name`      | VARCHAR(50) | UNIQUE, NOT NULL   | Name of the role (e.g., `User`, `Seller`).     |

---

### 2.4 `user_roles` Table

Junction table mapping users (or sellers) to one or multiple roles.

| Column Name | Data Type    | Constraints                  | Description                               |
| :---------- | :----------- | :--------------------------- | :---------------------------------------- |
| `user_id`   | VARCHAR(128) | FK references `users(id)`    | User ID (Firebase UID).                   |
| `role_id`   | INT          | FK references `roles(id)`    | Assigned role ID.                         |

> **Primary Key:** `(user_id, role_id)`

---

### 2.5 `sections` Table

Defines main application pages/views for navigation and interface access control.

| Column Name  | Data Type    | Constraints        | Description                                  |
| :----------- | :----------- | :----------------- | :------------------------------------------- |
| `id`         | INT          | PK, Auto Increment | Unique section identifier.                   |
| `name`       | VARCHAR(100) | UNIQUE, NOT NULL   | Display name (e.g., `Home`, `Seller Home`).  |
| `route_name` | VARCHAR(100) | UNIQUE, NOT NULL   | Route path (e.g., `/home`, `/seller/home`).  |

---

### 2.6 `role_section_grants` Table

Authorizes roles to access specific sections of the application.

| Column Name  | Data Type | Constraints                  | Description                                  |
| :----------- | :-------- | :--------------------------- | :------------------------------------------- |
| `role_id`    | INT       | FK references `roles(id)`    | Target role.                                 |
| `section_id` | INT       | FK references `sections(id)` | Accessible section.                          |

> **Primary Key:** `(role_id, section_id)`

---

### 2.7 `sub_sections` Table

Defines granular UI components/widgets within parent sections.

| Column Name    | Data Type    | Constraints        | Description                                   |
| :------------- | :----------- | :----------------- | :-------------------------------------------- |
| `id`           | INT          | PK, Auto Increment | Unique sub-section identifier.                |
| `name`         | VARCHAR(100) | UNIQUE, NOT NULL   | Human-readable name (e.g., `Search Bar`).     |
| `component_id` | VARCHAR(100) | UNIQUE, NOT NULL   | Component key (e.g., `widget_search`).       |

---

### 2.8 `section_sub_sections` Table

Maps reusable sub-sections (UI widgets) to parent sections.

| Column Name      | Data Type | Constraints                      | Description                               |
| :--------------- | :-------- | :------------------------------- | :---------------------------------------- |
| `section_id`     | INT       | FK references `sections(id)`     | Parent section.                           |
| `sub_section_id` | INT       | FK references `sub_sections(id)` | Included child component/widget.          |

> **Primary Key:** `(section_id, sub_section_id)`

---

## 3. Offloaded Components & Services

- **Authentication Providers:** Handled by **Firebase Auth** for both **Google Sign-In** and **Email / Password**.
- **Password Storage (`password_hash`):** Managed completely by **Firebase Auth** using scrypt/Bcrypt internally for email/password users. No plaintext or password hashes exist in PostgreSQL.
- **Session & Token Management (`tokens` table):** Managed by **Firebase Auth**. ID tokens (JWTs) and refresh tokens are issued and revoked through the Firebase Admin SDK.
- **User Document Sync:** When a user registers or logs in via Firebase Auth (Google or Email/Password), their profile document is saved to Firestore under `users/{uid}`, and a corresponding row is populated in PostgreSQL `users` with `id = uid` and `auth_provider` (`google.com` or `password`).
