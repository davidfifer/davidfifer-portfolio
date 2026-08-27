# David Fifer - Engineering Portfolio

<p align="center">
<img src="https://img.shields.io/badge/Java-21-ED8B00.svg?logo=openjdk&logoColor=white" />
<img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Spring%20Boot-3.0-6DB33F.svg?logo=springboot&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-Microservices-009688.svg?logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/OpenTelemetry-Tracing-orange.svg?logo=open-telemetry&logoColor=white" />
<img src="https://img.shields.io/badge/Jaeger-Trace%20UI-purple.svg?logo=jaeger&logoColor=white" />
<img src="https://img.shields.io/badge/Prometheus-Metrics-orange.svg?logo=prometheus&logoColor=white" />
<img src="https://img.shields.io/badge/Docker-Enabled-2496ED.svg?logo=docker&logoColor=white" />
<img src="https://img.shields.io/badge/PostgreSQL-15-336791.svg?logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/Distributed%20Systems-blueviolet" />
<img src="https://img.shields.io/badge/Observability-green" />
<img src="https://img.shields.io/badge/CLI-Tools-yellow" />
<img src="https://img.shields.io/badge/Data%20Engineering-blueviolet" />
<img src="https://img.shields.io/badge/Automation-red" />
<img src="https://img.shields.io/badge/License-MIT-green.svg" />
</p>

A curated collection of backend engineering, reliability-focused, automation, and data-processing projects built to
demonstrate clean architecture, modern tooling, and production‑grade development practices.
This repository serves as a unified portfolio showcasing work across Java, Spring Boot, Python, FastAPI microservices,
distributed tracing, observability tooling, CLI utilities, data cleaning pipelines, and Dockerized services.

Each project is designed to be practical, configurable, and easy to run, reflecting real-world engineering patterns such
as declarative configuration, layered architecture, strict validation, automated workflows, and end-to-end observability.

---

## Projects

### Notes API - Spring Boot + JWT + Docker

A fully containerized REST API demonstrating secure authentication, layered architecture, PostgreSQL persistence,
and automated testing. Use to create and manage notes. Built with Spring Boot 3, secured with JWT authentication,
and backed by PostgreSQL.

#### Key capabilities:

- JWT authentication
- CRUD operations
- Docker Compose orchestration
- Swagger UI documentation
- JUnit + Mockito test suite

---

### Distributed Tracing Demo - FastAPI + OpenTelemetry + Jaeger + Prometheus

A multi‑service FastAPI application demonstrating real distributed‑systems reliability patterns, including request
propagation, retry logic, chaos injection, metrics instrumentation, and full OpenTelemetry tracing.

#### Key capabilities:

- End‑to‑end OpenTelemetry tracing
- Jaeger UI span visualization & latency analysis
- Prometheus metrics (latency, error rates, request counts)
- Retry logic with exponential backoff
- Chaos‑mode fault injection (random delays + error simulation)
- Containerized observability stack (Jaeger + Prometheus + services)
- Structured logging with trace/span correlation IDs
- Configurable service behavior via environment variables

#### Demonstrates:

- Distributed‑systems fundamentals
- Reliability engineering patterns (retries, timeouts, chaos testing)
- Modern observability tooling
- Production‑grade architecture with declarative configs

---

### CSV Cleaning Utility - Python + Typer

A deterministic, configuration‑driven CSV cleaning pipeline built for data engineers and automation workflows. It
provides strict validation, dtype enforcement, profiling metrics, and a clean Typer CLI.

  #### Features include:

- Multi‑stage cleaning pipeline
- YAML/JSON configuration
- Numeric/date validation
- Missing‑value strategies
- Duplicate removal
- Row‑level filtering
- Profiling metrics

---

### File Sorting Utility - Python + argparse

A cross‑platform file‑organization tool that sorts files by extension or modified date, supports dry‑run previews, and
handles file locks safely. A predictable, configuration‑driven way to keep directories clean without manual cleanup or
brittle one‑off scripts.

#### Highlights:

- Extension‑based and date‑based sorting
- JSON configuration
- Dry‑run mode
- File‑lock detection (Windows + Unix)
- Verbose logging
- Automatic directory creation

---

## Purpose of This Repository

### This portfolio is designed to showcase:

- **Backend engineering expertise:** Spring Boot, JWT, layered architecture, PostgreSQL, Docker Compose.
- **Reliability & observability:** Distributed tracing, Prometheus metrics, structured logging, chaos testing.
- **Automation & tooling:** Python utilities, CLI design, configuration‑driven workflows.
- **Data engineering fundamentals:** Deterministic pipelines, validation, profiling, schema enforcement.
- **Software craftsmanship:** Clean code, documentation, testing, error handling, cross‑platform support.
- **Real‑world patterns:** Declarative configs, retry logic, logging pipelines, containerization.

Each project is self‑contained with its own README, installation instructions, architecture notes, and roadmap.

---

## Technologies Demonstrated

- Java 21, Spring Boot 3, Spring Security, JWT
- Python 3.10+, pandas, Typer, argparse
- Docker & Docker Compose
- PostgreSQL 15
- YAML/JSON configuration systems
- Logging pipelines
- Unit testing (JUnit 5, Mockito)
- CLI tooling
- Automation workflows
- Distributed tracing
- Prometheus metrics

---

## Repository Structure

```code
davidfifer-portfolio/
│
├── java/
│   └── notesapi/                   # Spring Boot + JWT + Docker Notes API
│
├── python/
│   ├── csv_data_cleaner/           # CSV Cleaning Utility (Typer + pandas)
│   ├── file_organizer/             # File Sorting Utility (argparse + JSON config)
│   └── distributed_tracing_demo/   # FastAPI + OpenTelemetry + Jaeger + Prometheus
```

---

## Author

David Fifer - [@AuthorLinkedIn](https://www.linkedin.com/in/david-b-fifer) - davidfifer47@gmail.com

---

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Licensed under the MIT License. See [LICENSE](LICENSE) for full terms.
