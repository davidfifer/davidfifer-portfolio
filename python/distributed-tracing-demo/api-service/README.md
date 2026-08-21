# API Service

The API Service is the second hop in the distributed‑tracing demo. It receives traced requests from the frontend,
creates additional spans, injects latency when chaos mode is enabled, and forwards work to the worker service. With
automated OpenTelemetry instrumentation and manually defined spans, the API provides a clear view of how trace context
is enriched as it moves deeper into the system.

This service demonstrates:

- How mid‑tier services participate in distributed traces
- How manual spans clarify service‑level behavior
- How latency injection affects downstream spans
- How errors propagate from the worker back through the API
- How Jaeger visualizes multi‑service trace hierarchies

---

## Overview

The API Service is a FastAPI application that:

- Accepts a traced request at `/process`
- Creates a manual span (`api.process`)
- Injects latency when chaos mode is enabled
- Calls the worker service using a traced outbound HTTP request
- Adds attributes describing chaos behavior
- Emits telemetry to the OpenTelemetry Collector

All tracing is exported via OTLP and can be visualized in Jaeger, Tempo, or any OTLP‑compatible backend.

---

## Features

- FastAPI application
- Uvicorn ASGI server
- Automated OpenTelemetry instrumentation
    - FastAPI inbound request spans
    - Requests outbound HTTP spans
- Manual spans for clarity
    - `api.process`
    - `api.call_worker`
- Chaos‑mode latency injection
- Error propagation from worker → API → frontend
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

The API automatically emits spans for:

- Inbound HTTP requests (GET `/process`)
- Outbound HTTP calls to the worker service

These spans include:

- HTTP method
- URL
- Status code
- Timing information
- Trace context propagation headers

### Manual Spans

Two manual spans provide semantic clarity:
- `api.process` - wraps the entire `/process` handler
- `api.call_worker` - wraps the outbound call to the worker service

These spans make the trace hierarchy easier to interpret in Jaeger.

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
- Error propagation when the worker fails
- Additional attributes describing chaos behavior
- Red spans in Jaeger when failures occur

When chaos is enabled:

```code
http://localhost:8001/process?chaos=true
```

You may see:

- `chaos.enabled = true`
- `latency.injected_ms = <value>`
- `error = true`
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
- Frontend service running
- Worker service running
- OpenTelemetry Collector accepting OTLP traces

---

## Running with Docker

### Required Environment Variables

- `OTEL_EXPORTER_OTLP_ENDPOINT` – OTLP HTTP endpoint of your OpenTelemetry Collector
- `WORKER_URL` - URL of the worker service

### Build the Image

```bash
docker build -t api-service .
```

### Run the Container

```bash
docker run -p 8001:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces \
  -e WORKER_URL=http://worker-service:8002 \
  api-service
```

### Access the Service

#### Normal mode:

```code
http://localhost:8001/process
```

#### Chaos mode:

```code
http://localhost:8001/process?chaos=true
```

---

## Example Traces

### Normal Request

- Clean hierarchy
- No errors
- No chaos attributes
- Moderate latency (worker call + API processing)

### Chaos Request

- Longer spans
- `latency.injected_ms` present
- Worker failure → red spans
- Error propagation visible across services
