# Worker Service

The Worker Service is the final hop in the distributed‑tracing demo. It receives traced requests from the API service,
performs simulated work, optionally injects latency, and may raise failures when chaos mode is enabled. With automated
OpenTelemetry instrumentation and a manually defined span, the worker shows how trace context behaves at the deepest
part of the system, including how failures propagate upstream.

This service demonstrates:

- How downstream services contribute to distributed traces
- How manual spans clarify worker‑level behavior
- How latency and failures affect upstream spans
- How error propagation appears in Jaeger
- How chaos mode simulates real‑world instability

---

## Overview

The Worker Service is a FastAPI application that:

- Accepts a traced request at `/work`
- Creates a manual span (`worker.work`)
- Injects latency when chaos mode is enabled
- Randomly raises failures to simulate instability
- Emits telemetry to the OpenTelemetry Collector

All tracing is exported via OTLP and can be visualized in Jaeger, Tempo, or any OTLP‑compatible backend.

---

## Features

- FastAPI application
- Uvicorn ASGI server
- Automated OpenTelemetry instrumentation
  - FastAPI inbound request spans
- Manual span for clarity
  - `worker.work`
- Chaos‑mode latency injection
- Chaos‑mode random failures
- Error propagation to API → frontend
- OTLP exporter to OpenTelemetry Collector
- Dockerized environment using `python:3.11-slim`

---

## Table of Contents

- [Tracing Behavior](#tracing-behavior)
- [Chaos Mode](#chaos-mode)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Running with Docker](#running-with-docker)
- [Example Traces](#example-traces)

---

## Tracing Behavior

### Automated Instrumentation

The worker automatically emits spans for:

- Inbound HTTP requests (GET `/work`)

These spans include:

- HTTP method
- URL
- Status code
- Timing information
- Trace context propagation headers

### Manual Span

One manual span provides semantic clarity:
  - `worker.work` — wraps the entire `/work` handler

This span makes the trace hierarchy easier to interpret in Jaeger.

### Trace Hierarchy (Normal Mode)

```code
frontend.start
    frontend.call_api
        api.process
            api.call_worker
                worker.work
```

---

## Chaos Mode

Chaos mode introduces:

- Random latency (`latency.injected_ms`)
- Random failures (`worker.failure = true`)
- Error propagation upstream
- Red spans in Jaeger when failures occur

When chaos is enabled:

```code
http://localhost:8002/work?chaos=true
```

You may see:

- `chaos.enabled = true`
- `latency.injected_ms = <value>`
- `worker.failure = true`
- `otel.status_code = ERROR`

Chaos mode is optional and defaults to false when the query parameter is omitted.

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
- API service running
- OpenTelemetry Collector accepting OTLP traces

---

## Running with Docker

### Required Environment Variables

- `OTEL_EXPORTER_OTLP_ENDPOINT` – OTLP HTTP endpoint of your OpenTelemetry Collector

### Build the Image

```bash
docker build -t worker-service .
```

### Run the Container

Start the service and pass the required environment variable:

```bash
docker run -p 8002:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces \
  worker-service
```

### Access the Service

#### Normal mode:

```code
http://localhost:8002/work
```

#### Chaos mode:

```code
http://localhost:8002/work?chaos=true
```

---

## Example Traces

### Normal Request

- Clean hierarchy
- No errors
- No chaos attributes
- Fast response

### Chaos Request

- Longer spans
- `latency.injected_ms` present
- Worker failure → red spans
- Error propagation visible across API → frontend
