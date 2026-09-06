# Deploying Fiti Backend to Google Cloud Run

This guide outlines how to containerize and deploy the **Fiti FastAPI** backend to Google Cloud Run, covering Docker setup, handling build-time vs. runtime keys, and secret management.

---

## 1. Project Files Overview

- **`Dockerfile`**: Multi-stage build using Python 3.12 and `uv`.
  - Installs production dependencies in a dedicated build stage.
  - Generates a minimal, hardened final runner image under a non-privileged `appuser`.
  - Binds Uvicorn dynamically to `0.0.0.0:${PORT:-8080}` as required by Google Cloud Run.
- **`.dockerignore`**: Ensures `.env`, `.git`, `.venv`, and sensitive credential files (`*firebase*.json`, `*.pem`, `*.key`) are never baked into the container image.

---

## 2. Build-Time vs. Runtime Keys

| Key Type | Execution Phase | Common Examples | Best Practice / Security Guideline |
| :--- | :--- | :--- | :--- |
| **Build-Time Keys** | During `docker build` | Private GitHub tokens, private npm/PyPI registry credentials | **NEVER store production secrets or database credentials at build time.** Any key added via `ENV` or `COPY` during build will be permanently readable in the image layers. |
| **Runtime Keys** | When the container starts on Cloud Run | Database URL (`CONNECTION_STRING`), Cloudinary secrets, Firebase credentials | Injected dynamically by Cloud Run using **Environment Variables** or **Google Secret Manager**. |

### When are Build-Time Keys used?
If your build needs to fetch dependencies from a private Git repo or artifact repository:
```dockerfile
# Dockerfile snippet (only if private repo access is needed)
RUN --mount=type=secret,id=pip_token \
    PIP_EXTRA_INDEX_URL=$(cat /run/secrets/pip_token) uv sync ...
```
And built with:
```bash
docker build --secret id=pip_token,src=./token.txt -t fiti-backend .
```
*(For standard open-source dependencies in `pyproject.toml`, build-time secrets are **not** needed).*

---

## 3. Configuring Runtime Secrets & Variables

The Fiti application expects the following configuration parameters:
- `CONNECTION_STRING`: PostgreSQL database connection URL (e.g. Supabase, Neon, or Cloud SQL).
- `ENVIRONMENT`: Set to `production`.
- `DEBUG`: Set to `False`.
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`.
- `FIREBASE_CREDENTIALS_JSON`: Optional when not using ADC.

### Step 3.1: Enable Required GCP Services
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

### Step 3.2: Store Sensitive Secrets in Google Secret Manager
Run the following commands to create secrets without storing them in plain text:

```bash
# 1. Database Connection String
echo -n "postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require" | \
  gcloud secrets create DB_CONNECTION_STRING --data-file=-

# 2. Cloudinary API Secret
echo -n "YOUR_CLOUDINARY_API_SECRET" | \
  gcloud secrets create CLOUDINARY_API_SECRET --data-file=-

# 3. Cloudinary API Key
echo -n "YOUR_CLOUDINARY_API_KEY" | \
  gcloud secrets create CLOUDINARY_API_KEY --data-file=-
```

### Step 3.3: Firebase Admin Authentication on Cloud Run

Choose **one** of the two approaches below:

#### Approach A: Google Application Default Credentials (ADC) — Recommended
Because Cloud Run runs natively in Google Cloud, `firebase_admin.initialize_app()` in `app/core/security.py` can automatically authenticate using the Cloud Run Service Account without any JSON file.

Grant the Cloud Run service account access:
```bash
# Replace with your GCP project ID and project number
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUM=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/firebaseauth.admin"
```
*(No `FIREBASE_CREDENTIALS_JSON` needs to be defined).*

#### Approach B: Firebase JSON from Secret Manager
If your Firebase project is under a separate GCP project, store the service account JSON in Secret Manager and expose it as an environment variable:

```bash
# 1. Store the JSON file in Secret Manager
gcloud secrets create firebase-credentials \
  --data-file="fiti-b0cb2-firebase-adminsdk-fbsvc-0182bfc133.json"

# 2. Bind the secret to the service via:
#    --set-secrets "FIREBASE_CREDENTIALS_JSON=firebase-credentials:latest"
```

---

## 4. Deploying to Cloud Run

Run the following command from the root directory of the project:

```bash
gcloud run deploy fiti-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=production,DEBUG=False,CLOUDINARY_CLOUD_NAME=your_cloud_name" \
  --set-secrets "CONNECTION_STRING=DB_CONNECTION_STRING:latest,CLOUDINARY_API_KEY=CLOUDINARY_API_KEY:latest,CLOUDINARY_API_SECRET=CLOUDINARY_API_SECRET:latest"
```

> **If using Approach B for Firebase:**
> Include the Firebase secret in the `--set-secrets` flag:
> ```bash
> --set-secrets "FIREBASE_CREDENTIALS_JSON=firebase-credentials:latest,CONNECTION_STRING=DB_CONNECTION_STRING:latest,..."
> ```

---

## 5. Verifying Deployment

Once deployed, Google Cloud Run will display the service URL:
```text
Service [fiti-backend] revision [fiti-backend-00001-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://fiti-backend-xxxxx-uc.a.run.app
```

You can verify the backend endpoints:
- **Health Check**: `https://fiti-backend-xxxxx-uc.a.run.app/api/v1/health`
- **Swagger Documentation**: `https://fiti-backend-xxxxx-uc.a.run.app/docs`
- **OpenAPI Schema**: `https://fiti-backend-xxxxx-uc.a.run.app/api/v1/openapi.json`
