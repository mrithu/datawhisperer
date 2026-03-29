#!/bin/bash
# =====================================================
# DataWhisperer - Cloud Run Deployment Script
# Run: chmod +x deploy.sh && ./deploy.sh
# =====================================================

set -e

echo "🔮 DataWhisperer — Cloud Run Deployment"
echo "========================================"

# ── Config ─────────────────────────────────────────
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="datawhisperer"
REGION="us-central1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "📦 Project:  ${PROJECT_ID}"
echo "🌍 Region:   ${REGION}"
echo "🐳 Image:    ${IMAGE}"
echo ""

# Check GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
  echo "❌ ERROR: GOOGLE_API_KEY environment variable is not set."
  echo "   Run: export GOOGLE_API_KEY=your_key_here"
  exit 1
fi

# ── Enable APIs ─────────────────────────────────────
echo "⚙️  Enabling required APIs..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  --project="${PROJECT_ID}"

# ── Build & Push Docker Image ───────────────────────
echo ""
echo "🏗️  Building Docker image..."
gcloud builds submit \
  --tag "${IMAGE}" \
  --project="${PROJECT_ID}" \
  .

echo ""
echo "✅ Image built and pushed: ${IMAGE}"

# ── Deploy to Cloud Run ─────────────────────────────
echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 120 \
  --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY},DB_PATH=/app/data/ecommerce.db" \
  --project="${PROJECT_ID}"

# ── Get Public URL ──────────────────────────────────
echo ""
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project="${PROJECT_ID}" \
  --format 'value(status.url)')

echo "========================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "🌐 Public URL: ${SERVICE_URL}"
echo ""
echo "Test it:"
echo "  curl ${SERVICE_URL}/health"
echo "========================================"
