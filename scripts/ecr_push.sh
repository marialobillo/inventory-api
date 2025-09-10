#!/usr/bin/env bash
set -euo pipefail

# === Config ===
AWS_REGION="${AWS_REGION:-eu-west-3}"
REPO_NAME="${REPO_NAME:-fastapi-inventory}"

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"

echo "Using: ACCOUNT_ID=${ACCOUNT_ID}"
echo "Using: ECR_URI=${ECR_URI}"

# Build (si usas Mac M1/M2)
export DOCKER_DEFAULT_PLATFORM="${DOCKER_DEFAULT_PLATFORM:-linux/amd64}"

# Requirements (si no tienes)
test -f requirements.txt || cat > requirements.txt <<'PY'
fastapi
uvicorn
sqlalchemy[asyncio]
aiosqlite
alembic
pydantic-settings
httpx
PY

# Create repo (idempotente)
aws ecr create-repository --repository-name "$REPO_NAME" --region "$AWS_REGION" || true

# Login
aws ecr get-login-password --region "$AWS_REGION" \
| docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Build & Push
docker build -t "$REPO_NAME:local" .
docker tag "$REPO_NAME:local" "$ECR_URI:latest"
docker push "$ECR_URI:latest"

# Verify
aws ecr list-images --repository-name "$REPO_NAME" --region "$AWS_REGION" --query 'imageIds[*].imageTag'
