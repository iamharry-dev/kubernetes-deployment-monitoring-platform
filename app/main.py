"""
Kubernetes Deployment and Monitoring Platform
---------------------------------------------
A small Flask service instrumented with Prometheus metrics. It exposes the
standard `/metrics` endpoint consumed by Prometheus and surfaced in Grafana,
and `/health` / `/ready` probes used by Kubernetes liveness/readiness checks.
"""

from __future__ import annotations

import os
import socket
import time

from flask import Flask, jsonify, Response, request
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

APP_NAME = os.getenv("APP_NAME", "k8s-monitoring-platform")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

app = Flask(__name__)

# --- Prometheus metrics ---------------------------------------------------
REQUEST_COUNT = Counter(
    "app_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency", ["endpoint"]
)
IN_PROGRESS = Gauge("app_in_progress_requests", "In-progress requests")
UPTIME = Gauge("app_uptime_seconds", "Seconds since process start")

_START_TIME = time.time()


@app.before_request
def _before():
    IN_PROGRESS.inc()


@app.after_request
def _after(response):
    IN_PROGRESS.dec()
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.path, status=response.status_code
    ).inc()
    return response


@app.route("/")
def root():
    UPTIME.set(time.time() - _START_TIME)
    return jsonify(
        {
            "service": APP_NAME,
            "version": APP_VERSION,
            "hostname": socket.gethostname(),
        }
    )


@app.route("/health")
def health():
    """Liveness probe."""
    return jsonify({"status": "healthy"}), 200


@app.route("/ready")
def ready():
    """Readiness probe."""
    return jsonify({"status": "ready"}), 200


@app.route("/work")
def work():
    """Simulated workload endpoint to generate latency metrics."""
    with REQUEST_LATENCY.labels(endpoint="/work").time():
        time.sleep(0.05)
    return jsonify({"status": "done"})


@app.route("/metrics")
def metrics():
    UPTIME.set(time.time() - _START_TIME)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
