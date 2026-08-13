# Worker Service

This service is part of a multi‑service distributed tracing demonstration designed to show how trace context flows
through multiple microservices under real operational conditions. When the frontend calls the worker’s `/work`
endpoint, the worker generates its own spans, simulates variable latency and occasional failures, and emits telemetry
that the collector aggregates into a single end‑to‑end trace. By running this service alongside the frontend, backend,
and collector, you can observe how downstream services contribute to a unified trace and how instrumentation reveals
system behavior under load, delay, and error scenarios.

---

## Overview

The Worker Service is a lightweight FastAPI application that exposes a `/work` endpoint and includes full OpenTelemetry
instrumentation for inbound operations. It simulates realistic work by introducing random delays and controlled
failures, allowing you to visualize how latency and exceptions appear in distributed traces. Traces are exported to an
OpenTelemetry Collector for visualization in Jaeger, Tempo, or similar backends.

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
- OpenTelemetry tracing (FastAPI instrumentation)
- OTLP HTTP exporter sending traces to an OpenTelemetry Collector
- Simulated latency (20% chance of 1.5s delay)
- Simulated failures (10% chance of raising an exception)

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
- OpenTelemetry Collector accepting OTLP traces
- Other services in the demo running (frontend, backend)

---

## Running with Docker

Running the Worker Service in Docker requires one environment variable:

- `OTEL_EXPORTER_OTLP_ENDPOINT` – OTLP HTTP endpoint of your OpenTelemetry Collector

This variable is mandatory for trace export.

### Build the Image

```bash
docker build -t worker-service .
```

### Run the Container

Start the service and pass the required environment variable:

```bash
docker run -p 8002:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318/v1/traces \
  worker-service
```

This command:

- Exposes the service on port 8002
- Points the OTLP exporter at the collector
- Ensures worker spans appear in the same distributed trace as the frontend and backend

### Accessing the Service

Once the container is running, call:

```text
http://localhost:8002/work
```

The `/work` endpoint:

- Generates a span in the worker service
- Introduces random latency or simulated failures
- Produces trace data visible in Jaeger, Tempo, or any OTLP‑compatible backend

---

## Dockerfile Overview

This service uses a simple Dockerfile that:

- sets the working directory
- installs dependencies
- copies the application source
- starts Uvicorn on `0.0.0.0:8000`

---

## Contributing

To contribute to the development of the worker-service:

1. Fork worker-service from https://github.com/davidfifer/davidfifer-portfolio/fork
2. Create your feature branch (git checkout -b feature-new)
3. Make your changes
4. Commit your changes (git commit -am 'Add new feature')
5. Push to the branch (git push origin feature-new)
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
