#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Build the Docker image, load it into a local kind cluster, and deploy.
# ---------------------------------------------------------------------------
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-monitoring}"
IMAGE="${IMAGE:-k8s-monitoring-platform:dev}"
OVERLAY="${OVERLAY:-k8s/overlays/dev}"

echo "==> Building image ${IMAGE}"
docker build -t "${IMAGE}" .

echo "==> Ensuring kind cluster '${CLUSTER_NAME}' exists"
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  kind create cluster --name "${CLUSTER_NAME}"
fi

echo "==> Loading image into kind"
kind load docker-image "${IMAGE}" --name "${CLUSTER_NAME}"

echo "==> Applying manifests (${OVERLAY})"
kubectl apply -k "${OVERLAY}"

echo "==> Waiting for rollout"
kubectl rollout status deployment/app-dev -n k8s-monitoring-dev --timeout=120s || true

echo "==> Deployment complete"
