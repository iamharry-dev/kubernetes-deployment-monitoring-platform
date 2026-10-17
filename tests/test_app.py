"""Unit tests for the monitored Flask application."""

import pytest

from app.main import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "service" in resp.get_json()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


def test_ready(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ready"


def test_metrics_exposes_prometheus_format(client):
    client.get("/")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "app_requests_total" in body
    assert "app_uptime_seconds" in body


def test_work_endpoint(client):
    resp = client.get("/work")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "done"
