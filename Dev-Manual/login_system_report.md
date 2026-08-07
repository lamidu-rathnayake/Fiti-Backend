# Fiti — Web User Login System Report

## Architecture Overview

Fiti uses a **Hybrid Auth Architecture** designed for a **Web Application** (e.g., Next.js, React, or Vue). The responsibility is split between two systems:

| Responsibility | Owner |
|---|---|
| Password hashing, session tokens, Google/OAuth popups, email auth | **Firebase Auth** (Google Web JS SDK) |
| Role profile (Client/Seller), measurements, shops, orders | **Fiti FastAPI Backend** (PostgreSQL) |

The backend **never stores passwords or emails**. It receives a **Firebase UID** — a unique ID string that Firebase assigns to every authenticated user — and creates a role-specific profile record in PostgreSQL around it.

---

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Frontend (Browser)                   │
│                    (e.g., Next.js / React)                  │
│                                                             │
│  Firebase Web JS SDK ←────────────────────────────────────  │
│  (Google OAuth popup / Email Auth handled in browser)       │
└────────────────────────┬─────────────────────┬──────────────┘
                         │                     │
                    (on sign-up)         (on sign-in)
                         │                     │
                         ▼                     ▼
             ┌───────────────────┐   ┌─────────────────────┐
             │  Fiti Backend     │   │  Fiti Backend       │
             │  FastAPI          │   │  FastAPI            │
             │                  │   │                     │
             │  POST /profiles/ │   │  GET /api/...       │
             │  client OR seller│   │  (uses Firebase UID │
             │  (first-time only)│   │  to fetch data)     │
             └────────┬──────────┘   └──────────┬──────────┘
                      │                          │
                      ▼                          ▼
             ┌──────────────────────────────────────────────┐
             │               PostgreSQL                      │
             │                                              │
             │   clients table         sellers table        │
             │   ┌────────────────┐   ┌──────────────────┐  │
             │   │ id (Firebase   │   │ id (Firebase UID)│  │
             │   │     UID) PK    │   │ nic_front        │  │
             │   │ created_at     │   │ nic_rear         │  │
             │   └────────────────┘   │ is_verified      │  │
             │                        └──────────────────┘  │
             └──────────────────────────────────────────────┘
```

---

## Scenario 1: New Web User Sign-Up (First Time)

> **Jane** visits `fiti.lk` on her desktop or mobile browser and wants to order a custom suit. She clicks "Sign up with Google".

### Step-by-step Web Flow

```
STEP 1: Firebase Authentication (Browser SDK — no backend involved)
────────────────────────────────────────────────────────────────────

Jane clicks "Sign up with Google" on the web app
        │
        ▼
Firebase Web JS SDK (`signInWithPopup` / `signInWithRedirect`)
opens Google OAuth popup
        │
        ▼
Google verifies Jane's Google account
        │
        ▼
Firebase Web SDK receives user credentials:
    Firebase UID: "abc123xyz"
    Email:        "jane@gmail.com"
    Name:         "Jane Perera"
    Provider:     "google.com"
        │
        ▼
Firebase SDK stores token in Browser IndexedDB / LocalStorage
```

```
STEP 2: Profile Registration (Web Browser → Fiti FastAPI Backend)
──────────────────────────────────────────────────────────────────

Web app extracts the Firebase UID from the `user` object
        │
        ▼
fetch('/api/v1/profiles/client', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ id: "abc123xyz" })
})
        │
        ▼
ManageProfileUseCase.register_client()
        │
        ├── Checks if clients.id = "abc123xyz" exists → NOT FOUND
        │
        ├── Creates Client entity:
        │     Client(id="abc123xyz")
        │
        └── Saves to PostgreSQL clients table:
              INSERT INTO clients (id) VALUES ('abc123xyz');
        │
        ▼
Response 201 Created:
{
  "id": "abc123xyz",
  "created_at": "2026-08-02T09:15:00Z"
}
```

```
STEP 3: Redirect & Web Session (Onboarding)
───────────────────────────────────────────

Web app receives 201 Created
Browser router redirects Jane to `/onboarding/measurements`
```

---

## Scenario 2: Returning Web User Login (Already Registered)

> **Jane** clears her browser cache or uses a new browser, visits `fiti.lk`, and clicks "Sign in with Google".

### Step-by-step Web Flow

```
STEP 1: Firebase Web Authentication
───────────────────────────────────

Jane clicks "Sign in with Google"
        │
        ▼
Firebase Web JS SDK (`signInWithPopup`) verifies credentials
        │
        ▼
Firebase Web SDK returns user object with same Firebase UID: "abc123xyz"
```

```
STEP 2: Profile Check (Web Browser → Fiti FastAPI Backend)
──────────────────────────────────────────────────────────

Web app calls profile registration endpoint:
fetch('/api/v1/profiles/client', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ id: "abc123xyz" })
})
        │
        ▼
ManageProfileUseCase.register_client()
        │
        ├── Checks if clients.id = "abc123xyz" exists → FOUND ✅
        │
        └── Raises ProfileAlreadyExistsError
              │
              ▼
        API returns 409 Conflict:
        {
          "detail": "Client profile for Firebase UID 'abc123xyz' already exists."
        }
        │
        ▼
Web frontend receives 409 → Profile already exists → RETURNING USER
        │
        ▼
Skip onboarding → Router redirects directly to `/dashboard` ✅
```

### Returning Web User Decision Logic (JavaScript / Next.js example)
```javascript
import { signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { auth } from "@/lib/firebase";

async function handleGoogleLogin() {
  try {
    const provider = new GoogleAuthProvider();
    const userCredential = await signInWithPopup(auth, provider);
    const uid = userCredential.user.uid;

    // Check / register profile on FastAPI backend
    const res = await fetch("/api/v1/profiles/client", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: uid }),
    });

    if (res.status === 201) {
      // NEW USER — Redirect to measurement onboarding
      router.push("/onboarding/measurements");
    } else if (res.status === 409) {
      // RETURNING USER — Redirect to main client dashboard
      router.push("/dashboard");
    }
  } catch (error) {
    console.error("Login failed:", error);
  }
}
```

---

## Scenario 3: New Web Seller/Tailor Registration

> **Rasheed** (a tailor) opens `fiti.lk/seller/register` on his browser.

```
STEP 1: Firebase Auth sign-up in browser
        Firebase UID assigned: "seller_uid_r99"

STEP 2: Upload NIC images directly from browser to Firebase Storage / S3 / Cloud Storage
        Returns:
          nic_front: "https://storage.googleapis.com/fiti/nic/front_r99.jpg"
          nic_rear:  "https://storage.googleapis.com/fiti/nic/rear_r99.jpg"

STEP 3: Register Seller Profile on FastAPI Backend

fetch('/api/v1/profiles/seller', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id: "seller_uid_r99",
    nic_front: "https://storage.googleapis.com/fiti/nic/front_r99.jpg",
    nic_rear:  "https://storage.googleapis.com/fiti/nic/rear_r99.jpg"
  })
})
        │
        ▼
Response 201:
{
  "id": "seller_uid_r99",
  "is_verified": false,    ← Admin verifies before shop activation
  "nic_front": "https://...",
  "nic_rear":  "https://..."
}

STEP 4: Redirect tailor to `/seller/dashboard` (showing "Verification Pending" banner)
```

---

## What Firebase Stores vs What PostgreSQL Stores

| Field | Firebase Auth (Web SDK) | PostgreSQL (FastAPI) |
|---|---|---|
| Email & Password | ✅ Yes | ❌ No |
| Display Name & Photo | ✅ Yes | ❌ No |
| Firebase UID | ✅ Yes | ✅ Yes (as Primary Key) |
| Role (client/seller) | ❌ No | ✅ clients / sellers table |
| Measurements | ❌ No | ✅ measurement_profile table |
| Shop details & location | ❌ No | ✅ shops table |
| Voice Notes & Images | ❌ No | ✅ clothing_requests & images |
| Orders, Bids, Payments | ❌ No | ✅ Full order flow tables |

---

## Web Security & Token Handling (Production Ready Guidelines)

1. **Session Management**: Firebase Web SDK manages token refresh (`getIdToken()`) automatically in the browser.
2. **Backend Authentication Middleware**: In production, every API call from the web frontend should attach the ID token:
   ```javascript
   const token = await auth.currentUser.getIdToken();
   fetch('/api/v1/orders/requests', {
     headers: {
       'Authorization': `Bearer ${token}`
     }
   })
   ```
3. **FastAPI Token Verification**: The backend verifies the token using the `firebase-admin` Python SDK:
   ```python
   # FastAPI Dependency
   async def get_current_user_uid(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
       decoded_token = auth.verify_id_token(credentials.credentials)
       return decoded_token['uid']
   ```

---

## Endpoints Summary

| Endpoint | Web Page / Trigger | Purpose |
|---|---|---|
| `POST /api/v1/profiles/client` | `/register` (First-time) | Register new client profile |
| `POST /api/v1/profiles/seller` | `/seller/register` | Register seller profile + NIC |
| `POST /api/v1/profiles/client` (returns 409) | `/login` (Returning) | Identifies returning client |
| `PUT /api/v1/profiles/client/{id}/measurements` | `/onboarding/measurements` | Save client measurements |
| `GET /api/v1/profiles/client/{id}/measurements` | `/profile` | Load client measurements |
