# Distributed Tracing Demo

A clean microservice system demonstrating distributed tracing, latency propagation, error propagation, and chaos mode
using FastAPI, OpenTelemetry, Jaeger, and Docker Compose.

---

## Overview

This project consists of three FastAPI microservices instrumented with OpenTelemetry:

- **frontend-service** — entrypoint, starts the trace
- **api-service** — adds latency, calls worker
- **worker-service** — performs work, sometimes slow or erroring
- **Jaeger** — collects and visualizes traces
- **Docker Compose** — orchestrates everything

The system demonstrates:

- Distributed tracing
- Trace context propagation
- Latency injection
- Error propagation
- Chaos mode
- Multi-service architecture

---

## Features

- **Distributed tracing** across three FastAPI microservices
- **OpenTelemetry instrumentation** (auto + manual spans)
- **Trace context propagation** through HTTP calls
- **Latency injection** for simulating slow services
- **Error propagation** from worker → API → frontend
- **Chaos mode** with randomized delays and failures
- **Jaeger visualization** of spans, timing, and errors
- **Docker Compose** orchestration for full local environment
- **Architecture + sequence diagrams** included in /docs
- **Curl examples** for testing and debugging

---

## Technologies

- **Python** (FastAPI microservices)
- **FastAPI** for lightweight service endpoints
- **OpenTelemetry** for tracing instrumentation
- **Jaeger** for trace collection + visualization
- **Docker Compose** for multi‑service orchestration
- **Requests** for service‑to‑service HTTP calls
- **Python logging** for structured logs
- **Shell / curl** for testing and debugging

---

## Table of Contents

- [Project Structure](#project-structure)
- [Running the System](#running-the-system)
- [Curl Examples](#curl-examples)
- [Architecture Diagram](#architecture-diagram)
- [Sequence Diagrams](#sequence-diagrams)
- [How Tracing Works](#how-tracing-works)
- [Screenshots](#screenshots)
- [Why This Project Matters](#why-this-project-matters)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [Author](#author)
- [Change Log](#change-log)
- [License](#license)

---

## Project Structure

```code
distributed-tracing-demo/
│
├── frontend-service/
│   ├── src/main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── api-service/
│   ├── src/main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── worker-service/
│   ├── src/main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── infra/
│   ├── docker-compose.yml
│   └── jaeger/config.yaml
│
└── docs/
    ├── diagrams/
    │   ├── services_architecture.png
    │   └── sequence.png
    └── screenshots/
        └── jaeger_trace_chaos_true.png
```

---

## Running the System

```bash
docker-compose up --build
```

### Hit the entrypoint:

```bash
curl http://localhost:8000/start
```

You should see a JSON response showing the full service chain.

---

## Curl Examples

### Basic request (no chaos)

```bash
curl "http://localhost:8000/start"
```

This triggers the full trace:

`frontend → api → worker` 
with no injected latency or errors.

### Chaos mode enabled

```bash
curl "http://localhost:8000/start?chaos=true"
```

Chaos mode introduces:

- Random latency at each service
- Random worker failures
- Trace attributes:
  - `chaos.enabled=true`
  - `latency.injected_ms=<value>`
  - `error=true (if failure occurs)`

### Run multiple chaos requests

```bash
for i in {1..10}; do curl -s "http://localhost:8000/start?chaos=true"; echo; done
```

### Call API service directly (debugging)

```bash
curl "http://localhost:8001/process?chaos=true"
```

### Call worker service directly (debugging)

```bash
curl "http://localhost:8002/work?chaos=true"
```

---

## Architecture Diagram

The distributed tracing demo consists of three FastAPI microservices orchestrated via Docker Compose and instrumented
with OpenTelemetry. Each service emits spans to Jaeger, enabling full visibility into latency and error propagation
across the system.

![Architecture](docs/diagrams/services_architecture.png)

**Flow Overview**

| Component            | Role                          | Key Features                      |
|----------------------|-------------------------------|-----------------------------------|
| **Frontend Service** | Entry point for user requests | Calls API Service, starts trace   |
| **API Service**      | Business logic layer          | Propagates trace, injects latency |
| **Worker Service**   | Task executor                 | Simulates slow/error responses    |
| **Jaeger**           | Trace collector + UI          | Visualizes spans and timing       |

---

## Sequence Diagrams

The following sequence illustrates how a single request travels through the system:

![Sequence](docs/diagrams/sequence.png)

1. User sends `GET/start` to Frontend Service.
2. Frontend Service calls API Service `/process`.
3. API Service calls Worker Service `/work`.
4. Worker Service performs work (may delay or fail).
5. Each service emits spans to Jaeger via OpenTelemetry.
6. Jaeger UI displays the full trace timeline.

---

## How Tracing Works

Distributed tracing in this project is powered by OpenTelemetry and visualized in Jaeger. Each service automatically
and manually emits spans that together form a complete trace of a request flowing through the system.

1. Automated Instrumentation

All services use OpenTelemetry auto‑instrumentation:

### FastAPI instrumentation

- FastAPI inbound request spans
- Requests outbound HTTP spans
- Automatic trace context propagation

2. Manual Spans

Each service adds custom spans:

- `frontend.start`, `frontend.call_api`
- `api.process`, `api.call_worker`
- `worker.work`

These include attributes such as:

- `chaos.enabled`
- `latency.injected_ms`
- `error`

3. Context Propagation

Trace context flows automatically:

```code
frontend.start
    frontend.call_api
        api.process
            api.call_worker
                worker.work
```

4. Chaos Mode

Chaos mode introduces:

- Random latency
- Random worker failures
- Error propagation

5. Error Propagation

Worker failures propagate upward:

- Worker span → red
- API span → red
- Frontend span → red

---

## Screenshots

Screenshots are stored under:

```directory
./docs/screenshots/
```

### Normal Mode Trace

Shows:

- Minimal latency
- Clean waterfall
- No chaos attributes


### Chaos Mode Trace

Shows:

- Injected latency
- Longer spans
- Chaos attributes
- Variability across requests

Example:

```directory
./docs/screenshots/jaeger_trace_chaos_true.png
```

### Error Propagation Trace

Shows:

- Worker failure
- API failure
- Frontend failure
- Red spans across the chain

---

## Why This Project Matters

This demo highlights real distributed systems concepts:

- Observability
- Diagnostics
- Reliability patterns
- Multi-service architecture
- Modern tooling
- Docker Compose orchestration
- OpenTelemetry best practices

## Contributing

To contribute to the project follow the below steps:

1. Fork from https://github.com/davidfifer/davidfifer-portfolio/fork
2. Create your feature branch (`git checkout -b feature-new`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature-new`)
6. Open a pull request

---

## Contributors

A huge thank you to everyone who has put their time and effort into improving this project.

| Name                  | GitHub                                                                | Role                      |
|-----------------------|-----------------------------------------------------------------------|---------------------------|
| **David Fifer**       | [@davidfifer](https://github.com/davidfifer)                          | Creator & Maintainer      |
| **Community Members** | [Open a PR](https://github.com/davidfifer/davidfifer-portfolio/pulls) | Features, fixes, feedback |

If you’d like to contribute, check out the [Contributing](#contributing) and submit a pull request.

---

## Author

David Fifer – [@AuthorLinkedIn](https://www.linkedin.com/in/david-b-fifer) – davidfifer47@gmail.com

---

## Change Log

| Version   | Notes           |
|-----------|-----------------|
| **1.0.0** | Initial release |

---

## License

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Licensed under the MIT License. See [LICENSE](LICENSE) for full terms.
