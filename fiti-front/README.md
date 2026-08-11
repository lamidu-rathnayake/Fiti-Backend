# FITI Frontend Application

FITI is a bespoke suiting portal built with **Next.js 16**, designed to connect high-net-worth clients with Master Tailors from Savile Row and beyond.

This repository contains the frontend application, which serves as the client-facing and tailor-facing digital interface.

## 🏗️ Architecture & Data Flow

The FITI application follows a modern decoupled architecture:

### 1. The Frontend (Next.js)
The frontend is purely a client-side application responsible for rendering the UI and handling user interactions. It does not store sensitive data or handle database operations directly.

### 2. Authentication (Firebase)
- **Identity Provider**: We use **Firebase Authentication** strictly as an Identity Provider (IdP).
- **Flow**: When a user logs in or registers, the frontend communicates directly with Firebase via the Client SDK. Firebase validates the credentials and returns a secure, short-lived **JWT (JSON Web Token)**.
- **No Firestore**: The frontend does not use Firestore or the Firebase Admin SDK.

### 3. The Backend (FastAPI + PostgreSQL)
- **Data Source**: All business logic, user profiles, shops, measurements, and order tracking data are managed by a separate **FastAPI** backend connected to a PostgreSQL database.
- **Secure Communication**: Whenever the frontend needs to fetch or submit data, it makes an HTTP request to the FastAPI backend. It attaches the Firebase JWT in the `Authorization: Bearer <token>` header.
- **Backend Verification**: The FastAPI backend receives the token, uses the Firebase Admin SDK to verify its authenticity, and then executes the requested database operation.

---

## 🚀 Getting Started

Follow these steps to set up the frontend application after cloning the repository.

### Prerequisites
- [Node.js](https://nodejs.org/en/) (v18 or higher recommended)
- The FITI FastAPI backend running locally (default: `http://localhost:8000`)
- A Firebase project with Web Authentication enabled

### 1. Install Dependencies
Navigate into the `fiti-front` directory and install the required npm packages:
```bash
cd fiti-front
npm install
```

### 2. Configure Environment Variables
Create a file named `.env.local` in the root of the `fiti-front` directory. You will need to populate it with your Firebase Web App configuration keys (found in your Firebase Console under Project Settings > General > Your Apps).

```env
# FastAPI Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Firebase Client Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-storage-bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
```

### 3. Run the Development Server
Start the Next.js development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

---

## 📁 Project Structure
- `/app`: Next.js App Router definitions and global layouts.
- `/components`: Reusable React components and main Page components (e.g., `ClientHomePage.tsx`, `LoginPage.tsx`).
- `/lib`: Utility functions and core configurations:
  - `firebase.ts`: Initializes the Firebase Client SDK.
  - `AuthContext.tsx`: React Context providing global user state using Firebase `onAuthStateChanged`.
  - `api.ts`: Helper functions mapping directly to FastAPI endpoints, automatically attaching the Firebase JWT to outgoing requests.
