
# ☁️ Cloud Images App

Academic project for the Cloud Computing course @ ESGTS

![Google Cloud](https://cdn.jsdelivr.net/gh/devicons/devicon/icons/googlecloud/googlecloud-original.svg)

---

## Features

- Upload and analyze images using Google Cloud Vision
- Store images in Google Cloud Storage
- Store metadata in Firestore (NoSQL)
- Dashboard to view, filter, download, and delete images
- Pagination for image browsing
- SweetAlert2 notifications and modern UI (Bootstrap 5)
- Download images and view all analysis details
- Health check endpoint `/health`

---

## 🖼️ Architecture Diagram

![Architecture Diagram](https://i.ibb.co/dwXf7j3N/diagram-export-6-1-2025-9-07-21-PM.png)


**Explanation:**

- User interacts with the Flask web app deployed on Cloud Run
- App uploads images to GCS (Cloud Storage)
- App requests image labeling from Cloud Vision API
- App saves metadata/results to Firestore
- Dashboard reads from Firestore & GCS to present data

---

## 📚 Mapping "Course Topics" ↔️ "Project Implementation"

| Course Topic                     | Project Implementation                            |
| -------------------------------- | ------------------------------------------------- |
| Cloud models (PaaS, CaaS, FaaS)  | Cloud Run (CaaS), Cloud Functions (optional)      |
| Buckets and cloud storage        | GCS for image storage                             |
| NoSQL Databases                  | Firestore for metadata                            |
| Cloud APIs                       | Cloud Vision API for analysis                     |
| CI/CD & GitHub integration       | GitHub Actions + Cloud Build for auto deployment  |
| Security, Service Accounts, Keys | GCP Service Account (JSON), secrets in CI         |
| Docker & containerization        | Dockerfile, container deploy to Cloud Run         |
| Frontend/UX                      | Bootstrap 5, SweetAlert2, modals, mobile friendly |
| DNS / Custom domain              | (Optional)                                        |
| Data Export / Interop            | Export options planned (CSV/JSON)                 |

---

## 🚀 CI/CD Guide – Automatic Deployment

### 1. **How It Works**

- Every `git push` to `main` triggers a GitHub Actions workflow
- Workflow authenticates with Google Cloud, builds a Docker image, and deploys to Cloud Run
- Deployment is fully automated: no manual steps required!

### 2. **GitHub Actions Workflow Example**

```yaml
name: Deploy to Google Cloud Run

on:
  push:
    branches: [ "main" ]

jobs:
  build-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      with:
        project_id: ${{ secrets.GCP_PROJECT }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        export_default_credentials: true

    - name: Build and push Docker image
      run: |
        gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT }}/image-analyzer:${{ github.sha }}

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy image-analyzer           --image gcr.io/${{ secrets.GCP_PROJECT }}/image-analyzer:${{ github.sha }}           --region ${{ secrets.GCP_REGION }}           --platform managed           --allow-unauthenticated           --memory 512Mi           --quiet
```

### 3. **Required GitHub Secrets**

- `GCP_PROJECT` (your Google Cloud project ID)
- `GCP_REGION` (example: `europe-west1`)
- `GCP_SA_KEY` (service account JSON key, base64 encoded)

### 4. **Steps to Deploy**

1. Make your changes locally and push to `main`
2. GitHub Actions workflow runs (see "Actions" tab)
3. After a few minutes, the app is rebuilt and redeployed automatically to Cloud Run
4. Visit your Cloud Run URL to see changes!

---

## 📈 Example Dashboard (with legend)

```
+----------------------+
|     Navigation Bar   |
+----------------------+
|   Gallery of Cards   |   ← Image previews, filename, labels, download/delete buttons
|  (Paginated, Modal)  |
+----------------------+
|  Pagination Control  |
+----------------------+
|       Footer         |
+----------------------+
```

- **Navbar**: Access to Home, Upload, Dashboard, About
- **Image Cards**: Preview, filename, label list with confidence scores, date/time, file size
- **Download/Delete**: Actions per image
- **Pagination**: Browse through images
- **Modal**: Preview enlarged image
- **SweetAlert2**: Success/error popups

---

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (e.g. with .env)
export GCS_BUCKET_NAME=your-bucket
export FIRESTORE_COLLECTION=analisadas

# Run locally
python app.py
```

---

## 🤝 Credits

- Developed by João Jacinto @ ESGTS - Cloud Computing
- Powered by Google Cloud Platform

---

## 📄 License

MIT License (see LICENSE)
