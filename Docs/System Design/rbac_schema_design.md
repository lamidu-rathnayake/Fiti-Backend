# Role-Based Access Control (RBAC) Database Schema

This document outlines the normalized and fine-tuned relational database schema for the user model, designed to manage interface visibility and session management efficiently.

## 1. `users` Table

Stores core account credentials and profile details. Includes flags for soft-deletion and audit timestamps.

| Column Name     | Data Type    | Constraints      | Description                                           |
| :-------------- | :----------- | :--------------- | :---------------------------------------------------- |
| `id`            | UUID         | PK               | Unique identifier (UUID is safer than INT for users). |
| `name`          |
| `age`           |
| `email`         | VARCHAR(255) | UNIQUE, NOT NULL | User's email address.                                 |
| `password_hash` | VARCHAR(255) | NOT NULL         | Hashed password.                                      |
| `is_active`     | BOOLEAN      | DEFAULT TRUE     | Allows disabling a user without deleting their data.  |
| `created_at`    | TIMESTAMP    | DEFAULT NOW()    | Account creation time.                                |
| `updated_at`    | TIMESTAMP    | DEFAULT NOW()    | Last time the profile was modified.                   |

## 1. `sellers` Table

Stores core account credentials and profile details. Includes flags for soft-deletion and audit timestamps.

| Column Name     | Data Type    | Constraints      | Description                                           |
| :-------------- | :----------- | :--------------- | :---------------------------------------------------- |
| `id`            | UUID         | PK               | Unique identifier (UUID is safer than INT for users). |
| `name`          |
| `age`           |
| `email`         | VARCHAR(255) | UNIQUE, NOT NULL | User's email address.                                 |
| `password_hash` | VARCHAR(255) | NOT NULL         | Hashed password.                                      |
| `is_active`     | BOOLEAN      | DEFAULT TRUE     | Allows disabling a user without deleting their data.  |
| `created_at`    | TIMESTAMP    | DEFAULT NOW()    | Account creation time.                                |
| `updated_at`    | TIMESTAMP    | DEFAULT NOW()    | Last time the profile was modified.                   |
| `nic_front`     |
| `nic_rear`      |

## 2. `roles` Table

Defines the types of roles available in the system.

| Column Name | Data Type   | Constraints        | Description                   |
| :---------- | :---------- | :----------------- | :---------------------------- |
| `id`        | INT         | PK, Auto Increment | Unique identifier.            |
| `name`      | VARCHAR(50) | UNIQUE, NOT NULL   | Role name (`User`, `Tailer`). |

## 3. `user_roles` Table

A junction table that maps users to their specific roles.

| Column Name | Data Type | Constraints               | Description        |
| :---------- | :-------- | :------------------------ | :----------------- |
| `user_id`   | UUID      | FK references `users(id)` | The user.          |
| `role_id`   | INT       | FK references `roles(id)` | The assigned role. |

> **Primary Key:** `(user_id, role_id)`

## 4. `sections` Table

Defines the main view components or pages in the application.

| Column Name  | Data Type    | Constraints        | Description                                  |
| :----------- | :----------- | :----------------- | :------------------------------------------- |
| `id`         | INT          | PK, Auto Increment | Unique identifier.                           |
| `name`       | VARCHAR(100) | UNIQUE, NOT NULL   | E.g., `Home`, `user Home`, `tailer Home`.    |
| `route_name` | VARCHAR(100) | UNIQUE, NOT NULL   | E.g., `/home`, `/user/home`, `/tailer/home`. |

## 5. `role_section_grants` Table

Controls authorization by mapping roles directly to the sections they are permitted to see.

| Column Name  | Data Type | Constraints                  | Description                    |
| :----------- | :-------- | :--------------------------- | :----------------------------- |
| `role_id`    | INT       | FK references `roles(id)`    | The role being granted access. |
| `section_id` | INT       | FK references `sections(id)` | The section they can access.   |

> **Primary Key:** `(role_id, section_id)`

## 6. `sub_sections` Table

Defines individual UI components or features within sections.

| Column Name    | Data Type    | Constraints        | Description                                |
| :------------- | :----------- | :----------------- | :----------------------------------------- |
| `id`           | INT          | PK, Auto Increment | Unique identifier.                         |
| `name`         | VARCHAR(100) | UNIQUE, NOT NULL   | E.g., `search bar`, `Dashboard`.           |
| `component_id` | VARCHAR(100) | UNIQUE, NOT NULL   | E.g., `widget_search`, `widget_dashboard`. |

## 7. `section_sub_sections` Table

Maps sub-sections to their parent views, supporting reusability across multiple parent sections.

| Column Name      | Data Type | Constraints                      | Description      |
| :--------------- | :-------- | :------------------------------- | :--------------- |
| `section_id`     | INT       | FK references `sections(id)`     | Parent section.  |
| `sub_section_id` | INT       | FK references `sub_sections(id)` | Child component. |

> **Primary Key:** `(section_id, sub_section_id)`

## 8. `tokens` Table

Manages authentication states, active sessions, or API tokens for logged-in users. Includes a revocation flag.

| Column Name  | Data Type    | Constraints               | Description                                             |
| :----------- | :----------- | :------------------------ | :------------------------------------------------------ |
| `id`         | UUID         | PK                        | Unique session/token identifier.                        |
| `user_id`    | UUID         | FK references `users(id)` | The owner of the token.                                 |
| `token_hash` | VARCHAR(500) | UNIQUE, NOT NULL          | Hashed version of the JWT/Session token (for security). |
| `is_revoked` | BOOLEAN      | DEFAULT FALSE             | Set to TRUE to instantly kill a session.                |
| `expires_at` | TIMESTAMP    | NOT NULL                  | Natural expiration time.                                |
| `created_at` | TIMESTAMP    | DEFAULT NOW()             | When the login occurred.                                |
