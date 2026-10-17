#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Smoke test the deployed application through port-forwarding.
# ---------------------------------------------------------------------------
set -euo pipefail

NAMESPACE="${NAMESPACE:-k8s-monitoring-dev}"
SERVICE="${SERVICE:-app-dev}"
LOCAL_PORT="${LOCAL_PORT:-8080}"

echo "==> Port-forwarding svc/${SERVICE} on ${LOCAL_PORT}"
kubectl port-forward -n "${NAMESPACE}" "svc/${SERVICE}" "${LOCAL_PORT}:80" >/dev/null 2>&1 &
PF_PID=$!
trap 'kill ${PF_PID} 2>/dev/null || true' EXIT
sleep 3

echo "==> GET /health"
curl -fsS "http://localhost:${LOCAL_PORT}/health"
echo
echo "==> GET /metrics (first 5 lines)"
curl -fsS "http://localhost:${LOCAL_PORT}/metrics" | head -n 5
echo

echo "==> Smoke test passed"
