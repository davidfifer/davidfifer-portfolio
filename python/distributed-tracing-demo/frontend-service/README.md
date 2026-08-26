# Frontend Service

The Frontend Service is the entry point of the distributed‑tracing demo. It exposes a `/start` endpoint, generates the
initial trace context, and forwards requests to the API service. With automated OpenTelemetry instrumentation and
manually defined spans, the frontend provides a clear view of how trace context is created, propagated, and enriched
across microservices.

This service demonstrates:

- How inbound HTTP requests generate root spans
- How outbound HTTP calls propagate trace context
- How manual spans add semantic clarity
- How chaos mode introduces latency and failures
- How Jaeger visualizes end‑to‑end traces

---

## Overview

The Frontend Service is a lightweight FastAPI application that:

- Accepts a request at `/start`
- Creates a manual span (`frontend.start`)
- Calls the API service using a traced outbound HTTP request
- Adds attributes describing chaos behavior
- Emits telemetry to the OpenTelemetry Collector
- Participates in chaos mode when enabled

All tracing is exported via OTLP and can be visualized in Jaeger, Tempo, or any OTLP‑compatible backend.

---

## Features

- FastAPI application
- Uvicorn ASGI server
- Automated OpenTelemetry instrumentation
  - FastAPI inbound request spans
  - Requests outbound HTTP spans
- Manual spans for clarity
  - `frontend.start`
  - `frontend.call_api`
- Chaos‑mode latency + error injection
- OTLP exporter to OpenTelemetry Collector
- Dockerized environment using `python:3.11-slim`
- **Prometheus metrics**
  - `frontend_chaos_requests_total` 
- **Additional span attributes**
  - `api.url`
  - `chaos.enabled`
  - `latency.injected_ms`
  - `error`
- Lifespan hooks for startup/shutdown

---

## Table of Contents

- [Tracing Behavior](#tracing-behavior)
- [Chaos Mode](#chaos-mode)
- [Metrics](#metrics)
- [Telemetry Export](#telemetry-export)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Running with Docker](#running-with-docker)
- [Example Traces](#example-traces)

---

## Tracing Behavior

### Automated Instrumentation

The frontend automatically emits spans for:

- Inbound HTTP requests (GET `/start`)
- Outbound HTTP calls to the API service

These spans include:

- HTTP method
- URL
- Status code
- Timing information
- Trace context propagation headers

### Manual Spans

Two manual spans provide semantic clarity:

- `frontend.start` - wraps the entire `/start` request handler
- `frontend.call_api` - wraps the outbound call to the API service

These spans make the trace hierarchy easier to read in Jaeger.

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
- Error propagation across services
- Red spans in Jaeger when failures occur
- Increments the `frontend_chaos_requests_total` Prometheus counter

When chaos is enabled:

```code 
http://localhost:8000/start?chaos=true
```

You may see:

- `chaos.enabled = true`
- `latency.injected_ms = <value>`
- `error = true`
- `otel.status_code = ERROR`

Chaos mode is essential for demonstrating how distributed traces behave under failure conditions.

---

## Metrics

The frontend exposes Prometheus metrics via `prometheus_fastapi_instrumentator`:

- `frontend_chaos_requests_total` - number of chaos-enabled requests
- Default FastAPI metrics (latency, request count, exceptions)

Metrics are available at:

```code
http://localhost:8000/metrics
```

### Prometheus Scraping Example

```yaml
scrape_configs:
  - job_name: 'frontend-service'
    static_configs:
      - targets: ['localhost:8000']
```

---

## Telemetry Export

Traces are exported to the OpenTelemetry Collector using OTLP/HTTP:

```code
OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
``` 

This allows visualization in:

- Jaeger
- Tempo
- Any OTLP‑compatible backend

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
- Worker service running
- OpenTelemetry Collector accepting OTLP traces

---

## Running with Docker

#### Required Environment Variables

- `OTEL_EXPORTER_OTLP_ENDPOINT` – OTLP HTTP endpoint of your OpenTelemetry Collector
- `BACKEND_URL` - URL of the API service

### Build the Image

```bash
docker build -t frontend-service .
```

### Run the Container

```bash
docker run -p 8000:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces \
  -e BACKEND_URL=http://backend-service:8001 \
  frontend-service
```

### Access the Service

#### Normal mode:

```code
http://localhost:8000/start
``` 

#### Chaos mode:

```code
http://localhost:8000/start?chaos=true
```

Chaos mode is optional and defaults to false when the query parameter is omitted.

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
- Error propagation visible across services
