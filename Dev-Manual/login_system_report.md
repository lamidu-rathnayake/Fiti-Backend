
# Fiti — Web Login, Firebase Authentication & Role Gateway Report

## Architecture Overview

Fiti uses Firebase Authentication for browser sign-in, Firestore for user profiles, and a FastAPI gateway for post-login role resolution. PostgreSQL is not used by the login endpoint.

| System Layer | Responsible Service | Description |
|---|---|---|
| **Authentication** | **Firebase Auth** | Handles Google SSO (`signInWithPopup`), Email & Password Auth (`signInWithEmailAndPassword`, `createUserWithEmailAndPassword`), session tokens, and security. |
| **Post-login gateway** | **FastAPI** | Verifies the Firebase ID token and resolves the user's role through `GET /api/v1/auth/me/role`. Returns HTTP 404 for new/unassigned users. |
| **User Profiles & Roles** | **Firebase Firestore DB** | Stores role (`client` or `tailor`/`seller`), personal profile data, contact details, and timestamps in the `users` collection. |
| **Login database usage** | **None in PostgreSQL** | The auth endpoint does not query PostgreSQL tables. |

---

## System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                     Next.js Frontend Browser                      │
│                                                                   │
│  [Google SSO]  or  [Email & Password Login / Register]            │
│                              │                                    │
│                              ▼                                    │
│                   Firebase Auth Web SDK                           │
│           (Generates Firebase UID & ID Token)                     │
└──────────────────────────────┬────────────────────────────────────┘
                               │
       ┌───────────────────────┴───────────────────────┐
       │                                               │
      ▼ (Returning Login)                             ▼ (New / Unassigned User)
   ┌─────────────────────────────────┐           ┌─────────────────────────────────┐
   │ 1. Get Firebase ID token (JWT)  │           │ 1. GET /api/v1/auth/me/role     │
   │ 2. GET /api/v1/auth/me/role     │           │    returns HTTP 404 Not Found  │
   │ 3. FastAPI verifies token       │           │ 2. Frontend catches 404         │
   │ 4. Resolves role from JWT or    │           │ 3. Redirects to /onboarding     │
   │    Firestore `users/{uid}`      │           │ 4. Pre-fills Google Auth info   │
   └────────────────┬────────────────┘           │ 5. Selects role & submits form  │
                    │                            │ 6. Writes `users/{uid}` via     │
                    ▼                            │    `setDoc(..., {merge: true})` │
   ┌─────────────────────────────────┐           └────────────────┬────────────────┘
   │ Return role and `redirect_to`   │                            │
   │ • client → /client/home         │                            │
   │ • tailor → /tailor/home         │                            │
   └────────────────┬────────────────┘                            │
                    └───────────────────┬─────────────────────────┘
                                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                       Firebase Firestore DB                       │
│                                                                   │
│ Collection: `users`                                               │
│ Document ID: `{uid}`                                              │
│                                                                   │
│ {                                                                 │
│   "uid": "abc123xyz",                                             │
│   "email": "user@example.com",                                    │
│   "displayName": "Alexander Wright",                              │
│   "role": "client",  // or "tailor"                               │
│   "phone": "+44 7911 123456",                                     │
│   "address": "42 Regent Street",                                  │
│   "city": "London",                                               │
│   "updatedAt": "server timestamp"                                 │
│ }                                                                 │
└───────────────────────────────────────────────────────────────────┘
```

---

## Supported Authentication Methods

### 1. Google OAuth (Google SSO)
- Handled via `signInWithPopup(auth, googleProvider)` in the browser.
- Automatically extracts user's `uid`, `email`, `displayName`, and `photoURL`.
- The frontend obtains the resulting Firebase ID token and sends it to FastAPI (`GET /api/v1/auth/me/role`) for role resolution.
- **New User Path**: If the user has not completed onboarding, the endpoint returns `404 Not Found`, causing the frontend to redirect to `/onboarding`.

### 2. Username (Email) & Password Authentication
- **Sign-Up**: `createUserWithEmailAndPassword(auth, email, password)` creates the Firebase Auth credential, followed by updating `displayName`.
- **Sign-In**: `signInWithEmailAndPassword(auth, email, password)` verifies credentials. The resulting Firebase ID token is then sent to FastAPI.

---

## Backend Auth Endpoint

### Request

```http
GET http://localhost:8000/api/v1/auth/me/role
Authorization: Bearer <firebase-id-token>
```

The Bearer value is the Firebase ID token (signed JWT). The frontend obtains it with `user.getIdToken()`.

### Backend Processing

1. FastAPI extracts the Bearer token.
2. Firebase Admin verifies its signature, issuer, audience, and expiry.
3. The backend extracts `uid`, `email`, and the optional `role` custom claim.
4. If the JWT has no role claim, the backend queries `users/{uid}` from Firestore.
5. **Role Found**: Returns HTTP 200 with the resolved role and redirect path:
   ```json
   {
      "uid": "abc123xyz",
      "email": "user@example.com",
      "role": "client",
      "redirect_to": "/client/home"
   }
   ```
6. **Role Not Found (New User)**: Returns HTTP 404 Not Found:
   ```json
   {
      "detail": "Role not found for user."
   }
   ```

---

## User Onboarding & Form Data Persistence (Firestore DB)

After completing authentication via Google SSO or Email/Password, new users complete their profile details on `/onboarding`. The frontend writes the document to Firestore DB using `setDoc` with `{ merge: true }`:

### Client Profile Registration Flow

```typescript
import { db } from "@/lib/firebase/config";
import { doc, setDoc, serverTimestamp } from "firebase/firestore";

// Called after UI form submission
async function handleClientFormSubmit(uid: string, formData: ClientFormData) {
  const userRef = doc(db, "users", uid);

  await setDoc(userRef, {
    uid: uid,
    email: formData.email,
    displayName: formData.fullName,
    role: "client",
    phone: formData.phone,
    address: formData.address,
    city: formData.city,
    updatedAt: serverTimestamp(),
  }, { merge: true });
}
```

### Tailor Profile Registration Flow

```typescript
import { db } from "@/lib/firebase/config";
import { doc, setDoc, serverTimestamp } from "firebase/firestore";

// Called after UI form submission
async function handleTailorFormSubmit(uid: string, formData: TailorFormData) {
  const userRef = doc(db, "users", uid);

  await setDoc(userRef, {
    uid: uid,
    email: formData.email,
    displayName: formData.fullName,
    role: "tailor",
    phone: formData.phone,
    address: formData.address,
    city: formData.city,
    shopName: formData.shopName,
    specialty: formData.specialty,
    updatedAt: serverTimestamp(),
  }, { merge: true });
}
```

---

## Scenario 1: New User Registration (Google SSO or Direct)

1. **User opens Login/Register page** (`/login` or `/register`).
2. **User authenticates**:
   - Clicks **"Continue with Google"** → Firebase Google popup succeeds.
3. **Role Gate Check**:
   - Frontend calls `GET /api/v1/auth/me/role`.
   - FastAPI returns `404 Not Found` because no role exists in JWT custom claims or Firestore document.
4. **Redirect to Onboarding**:
   - Frontend catches `404` and redirects to `/onboarding`.
   - Form pre-fills Google account details (`displayName`, `photoURL`).
5. **Form Submission & Firestore Persistence**:
   - User selects role (`client` or `tailor`) and submits details.
   - Frontend creates/merges Firestore document `users/{uid}` via `setDoc(..., { merge: true })`.
   - Frontend calls backend profile creation (`POST /api/v1/profiles/client` or `/tailor`).
6. **Final Redirection**:
   - Client → Redirected to `/client/home`
   - Tailor → Redirected to `/tailor/home`

---

## Scenario 2: Returning User Login (Step-by-Step)

1. **User opens Login page** (`/login`).
2. **User logs in** using Google SSO or Email/Password (`signInWithEmailAndPassword`).
3. **Firebase JWT Retrieval**:
   - Frontend calls `user.getIdToken()`.
4. **Backend Role Request**:
   - Frontend calls `GET /api/v1/auth/me/role` with `Authorization: Bearer <token>`.
5. **Backend Verification and Role Lookup**:
   - Firebase Admin verifies the token.
   - FastAPI reads custom claims or queries `users/{uid}` from Firestore.
6. **Frontend Routing**:
   - `tailor` → `/tailor/home`
   - `client` → `/client/home`
   - Unassigned / missing role (`404`) → `/onboarding`

---

## Firestore Database Schema Summary

### Collection: `users`
**Document ID**: `{uid}`

| Field Name | Type | Description |
|---|---|---|
| `uid` | string | Unique Firebase Authentication User ID |
| `email` | string | User's email address |
| `displayName` | string | Full Name (First + Last Name) |
| `role` | string | User role (`"client"` \| `"tailor"`) |
| `phone` | string | Contact / WhatsApp phone number |
| `address` | string | Street address |
| `city` | string | City |
| `shopName` | string | Shop name for tailor profiles |
| `specialty` | string | Specialty for tailor profiles |
| `updatedAt` | timestamp | Server timestamp when the profile was saved |

---

## Storage and Security Notes

1. Registration and onboarding write profile documents directly through the Firestore Web SDK using `setDoc` with `{ merge: true }` to prevent "No document to update" errors for new accounts.
2. Returning login uses FastAPI as the token-verification and role-resolution gateway.
3. The auth endpoint uses no PostgreSQL tables.
4. Firestore security rules must prevent users from assigning unauthorized roles to themselves.
5. The backend returns `404 Not Found` when a role is unassigned or missing in Firestore. This ensures new users are reliably directed to `/onboarding` rather than defaulting to `client`.
