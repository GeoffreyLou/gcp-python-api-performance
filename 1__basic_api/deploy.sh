#!/bin/bash
# Used to deploy the API to GCP Cloud Run

set -a            
source ../.env
set +a

# Debug : display environment variables
echo "GCP_PROJECT_ID=$GCP_PROJECT_ID"
echo "GCP_REGION=$GCP_REGION"
echo "GCP_GAR=$GCP_GAR"
echo "IMAGE_NAME=$IMAGE_NAME"

# Create Artifact Repository (if it doesn't exist)
gcloud artifacts repositories create $GCP_GAR \
  --project $GCP_PROJECT_ID \
  --repository-format=docker \
  --location=$GCP_REGION \
  --description="Docker repository for APIs" || echo "Artifact Repository $GCP_GAR already exists"

# Build and push image
docker build -t "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_GAR/$IMAGE_NAME:latest" . && \
docker push "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_GAR/$IMAGE_NAME:latest" && \

# Deploy as a Cloud Run Service
gcloud run deploy $IMAGE_NAME \
  --project $GCP_PROJECT_ID \
  --region $GCP_REGION \
  --memory 8Gi \
  --cpu 4 \
  --image "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_GAR/$IMAGE_NAME:latest" \
  --allow-unauthenticated \
  --platform managed