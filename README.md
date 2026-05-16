# Greeting & Computation Service

This repository contains a globally scalable, highly available API service built with FastAPI, containerized with Docker, and orchestratable via Kubernetes.

## Architecture

The application has been upgraded from a local CLI tool to a distributed API service:
* **Framework:** FastAPI (ASGI) for high-performance, asynchronous HTTP request handling.
* **Core Logic:** Decoupled business logic (`core.py`) from the presentation layer (`main.py`).
* **Containerization:** Rootless Dockerfile based on `python:3.12-slim` for secure, reproducible deployments.
* **Orchestration:** Kubernetes manifests provided for deployment with HA (multiple replicas, resource limits, readiness/liveness probes).

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application locally:
   ```bash
   uvicorn main:app --reload
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Docker

Build the image:
```bash
docker build -t greeting-app .
```

Run the container:
```bash
docker run -p 8000:8000 greeting-app
```

## Kubernetes Deployment

Deploy the manifests located in the `k8s/` directory:
```bash
kubectl apply -f k8s/
```
Note: Update the image registry in `k8s/deployment.yaml` and the host domain in `k8s/ingress.yaml` before deployment.
