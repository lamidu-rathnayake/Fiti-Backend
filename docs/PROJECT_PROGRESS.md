# Fiti Backend — Project Progress Report

**Date:** August 21, 2026

## Overview of Completed Work
We have completed a major backend refactoring initiative to decouple user profile data from Firebase Firestore and centralize it within the PostgreSQL database. Alongside the architectural migration, the project documentation has been thoroughly standardized and updated.

### 1. Architectural & Database Migration (Firebase to PostgreSQL)
*   **Centralized Profiles**: Previously, client and tailor profiles (contact info, address, specialty) were stored in Firebase's Firestore database, leading to fragmented queries. This data has been completely migrated to the PostgreSQL `clients` and `tailors` tables.
*   **Hybrid Identity Implementation**: Firebase is now used strictly as an Identity Provider (IdP) for authentication. The frontend passes the signed JWT Bearer Token, which contains the `uid`, `name`, `email`, and `picture`. 
*   **Database Schema Updates (`schema.sql`)**: 
    *   Added `display_name`, `email`, and `photo_url` directly derived from the Firebase JWT.
    *   Added legacy Firestore fields (`phone`, `city`, `address`) for clients.
    *   Added legacy Firestore fields (`phone`, `city`, `address`, `specialty`) for tailors and shops.

### 2. Codebase Refactoring
*   **Security & Auth (`security.py`)**: 
    *   Updated the gateway and auth decoders to correctly extract `name` and `picture` from the JWT claims to feed the profile onboarding process.
    *   Refactored the `require_role` dependency to fully replace Firestore DB role checks with PostgreSQL queries against the `user_roles` table. 
*   **Domain & Use Cases**: 
    *   Expanded Domain Entities (`Client`, `Tailor`, `Shop`) to encompass the new contact and profile fields.
    *   Updated `ManageProfileUseCase` to map all JWT data during new user registration, and automatically insert new users into the PostgreSQL `user_roles` table upon onboarding.
    *   Updated Data Transfer Objects (DTOs) and Pydantic Response Schemas (`ClientResponse`, `TailorResponse`).
*   **SQLAlchemy Repositories**: Modified the `create` and `update` logic to persist the expanded profile entities to PostgreSQL.
*   **Test Suite Integration**: Completely rewrote the integration test suite mocks (`test_api.py`) to support dynamic mocking of user identities across end-to-end API workflows. All 13 unit and integration tests successfully pass.

### 3. Documentation Standardization
*   **Restructuring**: Reorganized the historical `Dev-Manual` into a clean, standard `docs/` directory.
*   **Cleanup**: Deleted outdated setup plans and legacy login reports that referenced deprecated Firestore behavior.
*   **Standardization**: Capitalized all Markdown files for high visibility.
*   **Content Updates**: Rewrote the `PROJECT_STRUCTURE.md` and `ENTITY_DICTIONARY.md` to perfectly reflect the new Hybrid Identity model and the PostgreSQL tables, removing all claims that the database contains "zero user tables".

## Next Steps
*   **Supabase Database Rollout**: Execute the updated `ALTER TABLE` statements in the production Supabase instance to prepare for deployment.
*   **Frontend Alignment**: Update the frontend Next.js application to remove its legacy `setDoc` Firestore calls and align its onboarding forms strictly with the new backend API endpoints (`POST /api/v1/profiles/client` and `POST /api/v1/profiles/tailor`).
