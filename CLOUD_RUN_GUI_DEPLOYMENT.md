# Deploying Fiti Backend to Google Cloud Run via Google Cloud Console (GUI)

This step-by-step walkthrough guides you through deploying your **Fiti FastAPI** backend using the **Google Cloud Console web interface** (no CLI required).

---

## Prerequisites
1. Your project repository is pushed to **GitHub** (or GitLab/Bitbucket).
2. You have a Google Cloud account with an active project and billing enabled.
3. Your repository includes the newly created `Dockerfile` and `.dockerignore` files in the root folder.

---

## Step 1: Store Sensitive Keys in Secret Manager (GUI)

Instead of typing passwords into Cloud Run in plain text, save them securely in Secret Manager first.

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. In the top search bar, type **Secret Manager** and select it (enable the API if prompted).
3. Click **+ CREATE SECRET** for each of the following:

| Secret Name | Secret Value | Notes |
| :--- | :--- | :--- |
| `DB_CONNECTION_STRING` | `postgresql://user:pass@host:5432/dbname?sslmode=require` | Your PostgreSQL connection string |
| `CLOUDINARY_API_KEY` | Your Cloudinary API key | |
| `CLOUDINARY_API_SECRET` | Your Cloudinary API secret | |
| `FIREBASE_CREDENTIALS_JSON` *(Optional)* | Upload the `fiti-...-firebase-adminsdk-....json` file | Only needed if mounting the JSON file |

> **Tip:** When creating `FIREBASE_CREDENTIALS_JSON`, under **Secret value**, you can click **Upload file** and select your `.json` key file directly.

---

## Step 2: Grant Permissions to Cloud Run (IAM)

Cloud Run needs permission to read secrets from Secret Manager and authenticate Firebase users.

1. In the GCP Console, navigate to **IAM & Admin** > **IAM**.
2. Locate the default compute service account:
   `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`
3. Click the **Pencil icon** (Edit principal) on the right side.
4. Click **+ ADD ANOTHER ROLE** and add:
   - **Secret Manager Secret Accessor** (allows Cloud Run to read your secrets).
   - **Firebase Authentication Admin** (allows token verification without needing local JSON files).
5. Click **Save**.

---

## Step 3: Create the Cloud Run Service

1. Search for **Cloud Run** in the GCP Console search bar and select it.
2. Click **+ CREATE SERVICE** at the top.

### 3.1 Service Basics
- **Deployment platform**: Choose **Continuously deploy from a repository** (recommended).
- Click **SET UP WITH CLOUD BUILD**:
  - **Repository Provider**: Select **GitHub**.
  - Click **Authenticate** to authorize Google Cloud to access your GitHub account.
  - Select your repository (`.../Fiti`).
  - Branch: `main` (or your target branch).
  - Build Type: Select **Dockerfile**.
  - Source location: `/Dockerfile` (leave as default).
  - Click **Save**.
- **Service name**: Enter `fiti-backend`.
- **Region**: Choose a region close to your users (e.g. `us-central1`, `asia-south1`, etc.).
- **CPU allocation and pricing**: Select **CPU is only allocated during request processing** (most cost-effective / free tier eligible).
- **Ingress control**: Select **All** (Allows traffic from the internet).
- **Authentication**: Select **Allow unauthenticated invocations** (since this is a public REST API).

---

### 3.2 Configure Environment Variables & Secrets (Container Settings)

Expand the section labeled **Container, Networking, Security**:

#### Tab: Container
1. **Container port**: Enter `8080` (matches the Dockerfile default).
2. Under **Environment variables**, click **+ ADD VARIABLE** for non-sensitive values:
   - Name: `ENVIRONMENT` | Value: `production`
   - Name: `DEBUG` | Value: `False`
   - Name: `CLOUDINARY_CLOUD_NAME` | Value: `your_cloud_name`
   *(If you are mounting the Firebase JSON file as a secret volume in the next step, also add)*:
   - Name: `FIREBASE_CREDENTIALS_PATH` | Value: `/secrets/firebase.json`

3. Under **Secrets**, click **+ REFERENCE A SECRET**:
   - **Database Connection String**:
     - Secret: Select `DB_CONNECTION_STRING`
     - Reference method: Select **Expose as environment variable**
     - Environment variable name: `CONNECTION_STRING`
     - Version: `latest`
   - **Cloudinary API Key**:
     - Secret: Select `CLOUDINARY_API_KEY`
     - Reference method: **Expose as environment variable**
     - Environment variable name: `CLOUDINARY_API_KEY`
     - Version: `latest`
   - **Cloudinary API Secret**:
     - Secret: Select `CLOUDINARY_API_SECRET`
     - Reference method: **Expose as environment variable**
     - Environment variable name: `CLOUDINARY_API_SECRET`
     - Version: `latest`
   - *(Optional) Firebase JSON File (if not using native IAM/ADC)*:
     - Secret: Select `FIREBASE_CREDENTIALS_JSON`
     - Reference method: Select **Mount as volume**
     - Mount path: `/secrets`
     - Path within mount: `firebase.json`
     - Version: `latest`

---

## Step 4: Deploy & Verify

1. Click the blue **CREATE** button at the bottom of the page.
2. Google Cloud Build will automatically build your Docker image from GitHub and deploy it to Cloud Run. This typically takes 2–4 minutes.
3. Once a green checkmark appears, your service is live!
4. At the top of the page, copy the generated **Service URL** (e.g. `https://fiti-backend-xxxxxx-uc.a.run.app`).

### Test Endpoints in Your Browser:
- **Swagger Documentation**: `https://fiti-backend-xxxxxx-uc.a.run.app/docs`
- **Health Check**: `https://fiti-backend-xxxxxx-uc.a.run.app/api/v1/health`
- **OpenAPI Schema**: `https://fiti-backend-xxxxxx-uc.a.run.app/api/v1/openapi.json`
