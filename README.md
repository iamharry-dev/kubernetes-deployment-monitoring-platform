# ☸️ Kubernetes Deployment and Monitoring Platform

A production-style platform that packages a containerized application, deploys it to **Kubernetes** with **Kustomize** and **Helm**, and provides full observability with **Prometheus**, **Grafana**, and **Alertmanager** — automated end-to-end with **Jenkins** and **GitHub Actions**.

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)

---

## 📌 Overview

| Area | Tooling |
|------|---------|
| Application | Python / Flask, instrumented with `prometheus-client` |
| Containerization | Docker |
| Orchestration | Kubernetes (Deployment, Service, Ingress, HPA, PDB) |
| Config management | Kustomize (base + dev/prod overlays) & Helm chart |
| Monitoring | Prometheus + Grafana + Alertmanager (kube-prometheus-stack) |
| Local cluster | kind |
| CI/CD | Jenkins + GitHub Actions |

## 🏗️ Architecture

```
        ┌───────────────────────────────────────────────────────┐
        │                    Kubernetes Cluster                   │
        │                                                         │
        │   Ingress ──▶ Service ──▶ Deployment (HPA, 2..N pods)   │
        │                                    │  /metrics           │
        │                                    ▼                     │
        │   ┌───────────────┐      scrape    ┌───────────────┐    │
        │   │   Prometheus  │◀───────────────│   App Pods    │    │
        │   └──────┬────────┘                 └───────────────┘    │
        │          │ rules                                          │
        │          ▼                                                │
        │   ┌───────────────┐      datasource   ┌───────────────┐  │
        │   │ Alertmanager  │                   │    Grafana     │ │
        │   └───────────────┘                   └───────────────┘  │
        └───────────────────────────────────────────────────────┘
```

## 📁 Repository Structure

```
kubernetes-deployment-monitoring-platform/
├── app/
│   ├── main.py                 # Flask app + Prometheus metrics
│   └── requirements.txt
├── k8s/
│   ├── base/                   # Deployment, Service, Ingress, HPA, PDB
│   └── overlays/
│       ├── dev/                # 1 replica, :dev image
│       └── prod/               # 4 replicas, :stable image
├── helm/
│   └── app/                    # Helm chart (templates + values)
├── monitoring/
│   ├── prometheus.yml          # Scrape configuration
│   ├── alert-rules.yml         # Alerting rules
│   └── grafana-dashboard.json  # Importable dashboard
├── scripts/
│   ├── deploy-local.sh         # Build + kind load + apply
│   ├── install-monitoring.sh   # Install kube-prometheus-stack
│   └── smoke-test.sh           # Port-forward smoke test
├── tests/
│   └── test_app.py
├── Jenkinsfile
├── Dockerfile
└── README.md
```

## ✅ Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind](https://kind.sigs.k8s.io/) (local cluster)
- [Helm](https://helm.sh/docs/intro/install/) 3+
- (Optional) `kustomize`, `curl`

## 🚀 Getting Started

### 1. Run the app locally

```bash
cd app
pip install -r requirements.txt
python main.py
# -> http://localhost:8000/metrics
```

### 2. Build & deploy to a local kind cluster

```bash
bash scripts/deploy-local.sh
kubectl get pods -n k8s-monitoring-dev
```

The script builds the image, loads it into kind, and applies the dev overlay.

### 3. Deploy with Helm

```bash
helm install app helm/app --namespace k8s-monitoring --create-namespace
kubectl get all -n k8s-monitoring
```

### 4. Install monitoring (Prometheus + Grafana)

```bash
bash scripts/install-monitoring.sh
```

Then port-forward:

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80          # Grafana (admin/admin)
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Import `monitoring/grafana-dashboard.json` into Grafana to view request rate, latency, and uptime panels.

### 5. Smoke test

```bash
bash scripts/smoke-test.sh
```

## 📊 Observability

The app exposes Prometheus metrics at `/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `app_requests_total` | Counter | Requests by method, endpoint, status |
| `app_request_latency_seconds` | Histogram | Request latency |
| `app_in_progress_requests` | Gauge | Concurrent requests |
| `app_uptime_seconds` | Gauge | Process uptime |

**Alerts** (`monitoring/alert-rules.yml`): `HighRequestRate`, `HighLatency`, `PodDown`.

## 🔄 CI/CD

- **GitHub Actions** (`.github/workflows/ci.yml`): lint, run unit tests, validate Kustomize + Helm manifests, then build and push the image to GHCR.
- **Jenkins** (`Jenkinsfile`): Checkout → Lint & Test → Build → Validate Manifests → Deploy → Verify.

## 🔐 Security & Reliability

- Non-root container, dropped Linux capabilities
- Liveness + readiness probes
- Rolling updates (`maxUnavailable: 0`)
- Horizontal Pod Autoscaler (CPU-based) and Pod Disruption Budget
- Resource requests/limits defined

## 📄 License

Released under the MIT License.

---

⭐ If you find this useful, please consider giving it a star.
