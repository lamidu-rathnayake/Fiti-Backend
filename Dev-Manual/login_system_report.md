# Fiti — Web User Login & Firestore Profile System Report

## Architecture Overview

Fiti uses a **Firebase-Native Auth & Firestore User Profile Architecture** designed for the **Next.js Web Application**. The system manages user authentication, account details, and roles entirely through Firebase services:

| System Layer | Responsible Service | Description |
|---|---|---|
| **Authentication** | **Firebase Auth** | Handles Google SSO (`signInWithPopup`), Email & Password Auth (`signInWithEmailAndPassword`, `createUserWithEmailAndPassword`), session tokens, and security. |
| **User Profiles & Roles** | **Firebase Firestore DB** | Stores user role (`client`, `seller`, `admin`), personal profile data, contact details, and timestamp records in the `users` collection. **No user profile data is stored in PostgreSQL.** |

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
       ▼ (First-Time Registration)                     ▼ (Returning Login)
┌───────────────────────────────────────┐     ┌─────────────────────────────────┐
│ 1. Fill Profile Form in UI            │     │ 1. Fetch User Doc from          │
│    (Name, Phone, Address, Role)       │     │    Firestore (`users/{uid}`)    │
│ 2. Save directly to Firestore DB      │     │ 2. Read `role` field            │
│    `doc(db, "users", uid)`            │     │ 3. Redirect to role dashboard:  │
│ 3. Redirect to Dashboard              │     │    • client  → /client/home     │
│    • client  → /client/home           │     │    • seller  → /seller/dashboard│
│    • seller  → /seller/dashboard      │     │    • admin   → /admin/dashboard │
└──────────────────┬────────────────────┘     └────────────────┬────────────────┘
                   │                                           │
                   └───────────────────┬───────────────────────┘
                                       │
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
│   "role": "client",  // or "seller" / "admin"                     │
│   "phone": "+44 7911 123456",                                     │
│   "address": "42 Regent Street",                                  │
│   "city": "London",                                               │
│   "gender": "Male",                                               │
│   "age": 28,                                                      │
│   "createdAt": "2026-08-13T10:00:00Z"                             │
│ }                                                                 │
└───────────────────────────────────────────────────────────────────┘
```

---

## Supported Authentication Methods

### 1. Google OAuth (Google SSO)
- Handled via `signInWithPopup(auth, googleProvider)` in the browser.
- Automatically extracts user's `uid`, `email`, `displayName`, and `photoURL`.
- If the user doc does not exist in Firestore, user is routed to the role onboarding form to complete profile registration.

### 2. Username (Email) & Password Authentication
- **Sign-Up**: `createUserWithEmailAndPassword(auth, email, password)` creates the Firebase Auth credential, followed by updating `displayName`.
- **Sign-In**: `signInWithEmailAndPassword(auth, email, password)` verifies credentials and logs the user in.

---

## User Onboarding & Form Data Persistence (Firestore DB)

After completing authentication via Google SSO or Email/Password, the user fills out their profile details in the UI form. The frontend writes this document directly into Firestore DB:

### Client Profile Registration Flow

```typescript
import { db } from "@/lib/firebase";
import { doc, setDoc, serverTimestamp } from "firebase/firestore";

// Called after UI form submission
async function handleClientFormSubmit(uid: string, formData: ClientFormData) {
  const userRef = doc(db, "users", uid);

  await setDoc(userRef, {
    uid: uid,
    email: formData.email,
    displayName: `${formData.firstName} ${formData.lastName}`,
    role: "client",
    phone: formData.phone,
    address: formData.address,
    city: formData.city,
    gender: formData.gender,
    age: Number(formData.age),
    createdAt: serverTimestamp(),
  }, { merge: true });
}
```

### Seller Profile Registration Flow

```typescript
import { db } from "@/lib/firebase";
import { doc, setDoc, serverTimestamp } from "firebase/firestore";

// Called after UI form submission
async function handleSellerFormSubmit(uid: string, formData: SellerFormData) {
  const userRef = doc(db, "users", uid);

  await setDoc(userRef, {
    uid: uid,
    email: formData.email,
    displayName: `${formData.firstName} ${formData.lastName}`,
    role: "seller",
    phone: formData.phone,
    address: formData.address,
    city: formData.city,
    bio: formData.bio || "",
    isVerified: false,
    createdAt: serverTimestamp(),
  }, { merge: true });
}
```

---

## Scenario 1: New User Registration (Step-by-Step)

1. **User opens Login/Register page** (`/login` or `/register`).
2. **User selects Auth Method**:
   - Option A: Clicks **"Sign up with Google"** → Google popup authenticates user → Returns `Firebase User` (`uid`).
   - Option B: Enters **Email & Password** + clicks **Register** → `createUserWithEmailAndPassword` creates user → Returns `Firebase User` (`uid`).
3. **Form Completion in UI**:
   - User enters name, contact number, address, and selects role (`client` or `seller`).
4. **Firestore Storage**:
   - Frontend executes `setDoc(doc(db, "users", uid), profileData)`.
   - Data stored in Firestore DB (`users/{uid}`) with assigned `role`.
5. **Redirection**:
   - Client → Redirected to `/client/home`
   - Seller → Redirected to `/register/seller/shop` / `/seller/dashboard`

---

## Scenario 2: Returning User Login (Step-by-Step)

1. **User opens Login page** (`/login`).
2. **User logs in** using Google SSO or Email/Password (`signInWithEmailAndPassword`).
3. **Firestore Role Lookup**:
   - App checks Firestore DB: `getDoc(doc(db, "users", user.uid))`.
4. **Automatic Routing based on Firestore `role`**:
   - If `role === "admin"` → Redirect to `/admin/dashboard`
   - If `role === "seller"` → Redirect to `/seller/dashboard`
   - If `role === "client"` → Redirect to `/client/home`
   - If profile document does not exist yet → Redirect to `/register` onboarding form.

---

## Firestore Database Schema Summary

### Collection: `users`
**Document ID**: `{uid}`

| Field Name | Type | Description |
|---|---|---|
| `uid` | string | Unique Firebase Authentication User ID |
| `email` | string | User's email address |
| `displayName` | string | Full Name (First + Last Name) |
| `role` | string | User role (`"client"` \| `"seller"` \| `"admin"`) |
| `phone` | string | Contact / WhatsApp phone number |
| `address` | string | Street address |
| `city` | string | City |
| `gender` | string | Gender (for client profiles) |
| `age` | number | Age (for client profiles) |
| `bio` | string | Seller description / bio |
| `isVerified` | boolean | Verification flag for seller accounts |
| `createdAt` | timestamp | Server timestamp when profile was saved |

---

## Advantages of Firestore DB Storage over Postgres for Users & Roles

1. **Direct Web SDK Access**: Fast client-side reads/writes via standard Firebase Firestore rules without needing custom backend ORM mapping for user metadata.
2. **Real-time State Synchronization**: `onAuthStateChanged` combined with `onSnapshot` allows immediate UI updates when roles or profile details change.
3. **Seamless Multi-Role Security Rules**: Security rules can check `request.auth.uid` against `resource.data.role` directly inside Firestore Rules.
