#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Install the kube-prometheus-stack (Prometheus + Grafana + Alertmanager)
# ---------------------------------------------------------------------------
set -euo pipefail

NAMESPACE="${NAMESPACE:-monitoring}"
RELEASE="${RELEASE:-monitoring}"

echo "==> Adding prometheus-community repo"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "==> Installing kube-prometheus-stack into '${NAMESPACE}'"
helm upgrade --install "${RELEASE}" prometheus-community/kube-prometheus-stack \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  --set grafana.adminPassword=admin \
  --wait

echo "==> Applying alert rules"
kubectl apply -n "${NAMESPACE}" -f monitoring/alert-rules.yml || true

echo
echo "Grafana:  kubectl port-forward -n ${NAMESPACE} svc/${RELEASE}-grafana 3000:80"
echo "Prometheus: kubectl port-forward -n ${NAMESPACE} svc/${RELEASE}-kube-prometheus-prometheus 9090:9090"
