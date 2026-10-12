"""Small Flask web app used to demonstrate a DevSecOps CI/CD pipeline.

Endpoints
    /          -> welcome message (JSON)
    /health    -> health check used by Docker, load balancers and monitoring
    /api/info  -> build/version information
    /metrics   -> Prometheus metrics (request count + latency)
"""
import os
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

REQUEST_COUNT = Counter(
    "app_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)


@app.before_request
def _start_timer():
    request.environ["_start_time"] = time.perf_counter()


@app.after_request
def _record_metrics_and_harden(response):
    """Record Prometheus metrics and add basic security headers."""
    start = request.environ.get("_start_time")
    endpoint = request.path
    if start is not None:
        REQUEST_LATENCY.labels(endpoint).observe(time.perf_counter() - start)
    REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()

    # Security headers (these also keep the OWASP ZAP baseline scan clean)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/")
def index():
    return jsonify(message="Hello from the DevSecOps CI/CD demo app", version=APP_VERSION)


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/api/info")
def info():
    return jsonify(app="devsecops-flask-app", version=APP_VERSION)


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    # Local development only. In Docker the app is served by gunicorn.
    app.run(host="127.0.0.1", port=5000)
