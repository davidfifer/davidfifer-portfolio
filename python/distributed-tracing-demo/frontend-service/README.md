# Frontend Service

This service is part of a multi‑service distributed tracing demonstration designed to show how trace context flows
through a real request path. When a client calls `/start`, the frontend generates an initial span, performs an outbound
HTTP request to the backend service, and emits telemetry that the collector aggregates into a single end‑to‑end trace. 
By running this service alongside the backend and collector, you can observe how microservices participate in a shared
trace and how instrumentation across frameworks and libraries contributes to a unified view of system behavior.

---

## Overview

The Frontend Service is a lightweight FastAPI application that exposes a `/start` endpoint and forwards requests to a
backend API. It includes full OpenTelemetry instrumentation for inbound and outbound operations, enabling trace
propagation across services. Traces are exported to an OpenTelemetry Collector for visualization in Jaeger, Tempo, or
similar backends.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Running with Docker](#running-with-docker)
- [Dockerfile Overview](#dockerfile-overview)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [Author](#author)
- [Change Log](#change-log)
- [License](#license)

---

## Features

- FastAPI application structure
- Uvicorn ASGI server
- Dockerized environment using `python:3.11-slim`
- Dependency installation via `requirements.txt`
- OpenTelemetry tracing (FastAPI + Requests instrumentation)
- OTLP exporter sending traces to an OpenTelemetry Collector

---

## Project Structure

```text
.
├── src
│   ├── __init__.py
│   ├── main.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Docker installed
- Backend API service running and reachable
- OpenTelemetry Collector accepting OTLP traces

---

## Running with Docker

Running the Frontend Service in Docker requires two environment variables:

- `OTEL_EXPORTER_OTLP_ENDPOINT` - OTLP gRPC endpoint of your OpenTelemetry Collector
- `BACKEND_URL` - the reachable URL of the backend service this frontend calls

These variables are mandatory for trace export and request forwarding.

### Build the Image

```bash
docker build -t frontend-service .
```

### Run the Container

Start the service and pass the required environment variables:

```bash
docker run -p 8000:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317 \
  -e BACKEND_URL=http://backend-service:8001 \
  frontend-service
```

This command:

- Exposes the service on port 8000
- Points the OTLP exporter at the collector
- Directs outbound requests to the backend service
- Ensures trace context flows across the full request path

### Accessing the Service

Once the container is running, call:

```text
http://localhost:8000/start
``` 

The `/start` endpoint:

- Creates an initial span in the frontend
- Sends a traced HTTP request to the backend
- Produces a unified distributed trace visible in Jaeger, Tempo, or any OTLP‑compatible backend

---

## Dockerfile Overview

This service uses a simple Dockerfile that:

- Sets the working directory
- Installs dependencies
- Copies the application source
- Starts Uvicorn on `0.0.0.0:8000`

---

## Contributing

To contribute to the development of the frontend-service:

1. Fork frontend-service from https://github.com/davidfifer/davidfifer-portfolio/fork
2. Create your feature branch (`git checkout -b feature-new`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature-new`)
6. Open a pull request

---

## Contributors

A huge thank you to everyone who has put their time and effort into improving this project.

| **Name**              | **GitHub**                                                            | **Contributions**                  |
|-----------------------|-----------------------------------------------------------------------|------------------------------------|
| **David Fifer**       | [@davidfifer](https://github.com/davidfifer)                          | Creator, architect, and maintainer |
| **Community Members** | [Open a PR](https://github.com/davidfifer/davidfifer-portfolio/pulls) | Features, fixes, feedback          |

If you’d like to contribute, check out the [Contributing](#contributing) and submit a pull request.

---

## Author

David Fifer – [@AuthorLinkedIn](https://www.linkedin.com/in/david-b-fifer) – davidfifer47@gmail.com

---

## Change Log

- 0.0.1
    * First working version

---

## License

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Licensed under the MIT License. See [LICENSE](LICENSE) for full terms.
