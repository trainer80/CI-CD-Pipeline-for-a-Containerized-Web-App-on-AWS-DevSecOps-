import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest  # noqa: E402
from app import app  # noqa: E402


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_index_returns_message(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.get_json()


def test_health_is_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_info_has_version(client):
    resp = client.get("/api/info")
    assert resp.status_code == 200
    assert "version" in resp.get_json()


def test_security_headers_present(client):
    resp = client.get("/")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in resp.headers


def test_metrics_endpoint_exposes_counter(client):
    client.get("/health")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"app_requests_total" in resp.data
