# Distributed Job Scheduler

<p align="center">
  <img src="https://img.shields.io/badge/Java-17-blue?logo=openjdk&logoColor=white" alt="Java 17">
  <img src="https://img.shields.io/badge/Spring%20Boot-3-6DB33F?logo=springboot&logoColor=white" alt="Spring Boot">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL Database">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/Flyway-Migrations-CC0200" alt="Flyway Migrations">
  <img src="https://img.shields.io/badge/Micrometer-Metrics-brightgreen" alt="Micrometer">
  <img src="https://img.shields.io/badge/Processing-Asynchronous-orange" alt="Asynchronous">
  <img src="https://img.shields.io/badge/Retry-Exponential%20Backoff-red" alt="Retry Exponential">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
</p>

A distributed job scheduling system built with Java, Spring Boot, PostgreSQL, and Docker Compose.

This project demonstrates core backend engineering concepts including asynchronous job processing, distributed
coordination, job lifecycle management, retry handling, exponential backoff, persistence, and containerized services.

---

## Overview

The Distributed Job Scheduler is a multi-service backend application that allows users to submit asynchronous jobs
for processing.

Jobs are persisted in PostgreSQL and executed by a separate worker service. The system supports job lifecycle
management, retries with exponential backoff, failure handling, metrics collection, and containerized deployment
using Docker Compose.

This project was built to explore distributed systems concepts commonly found in production backend platforms,
including background processing, state management, reliability patterns, and service-to-service coordination.

---

## Technology Stack

- Java 17
- Spring Boot 3
- Spring Data JPA
- PostgreSQL
- Flyway
- Docker
- Docker Compose
- Micrometer

---

## Quick Start

### Clone the repository:

```shell
git clone https://github.com/davidfifer/davidfifer-portfolio.git
cd davidfifer-portfolio/java/distributed-job-scheduler
```

### Build and start all services:

```shell
docker compose up --build
```

### Once the services are running:

- Scheduler API: http://localhost:8080
- PostgreSQL: localhost:5432

---

## Architecture

The system consists of three components:

```text
              +---------------------+
              |  Scheduler Service  |
              |      REST API       |
              +----------+----------+
                         |
                         |
                         v
                 +---------------+
                 | PostgreSQL DB |
                 +---------------+
                         ^
                         |
                         |
              +----------+----------+
              |   Worker Service    |
              | Poll + Execute Jobs |
              +---------------------+
```

### Scheduler Service

Responsible for:

- Accepting job submissions
- Persisting jobs to PostgreSQL
- Exposing job status endpoints
- Managing job metadata

### PostgreSQL

Stores:

- Job payloads
- Job state
- Attempt counts
- Retry scheduling information
- Creation timestamps

### Worker Service

Responsible for:

- Polling for runnable jobs
- Claiming jobs for execution
- Executing work
- Updating job status
- Applying retry and backoff logic
- Recording execution metrics

---

## Features

### Job Lifecycle

```text
PENDING → RUNNING → SUCCESS

PENDING → RUNNING → FAILED
                   ↓
                 RETRY
                   ↓
                PENDING

FAILED (after max retry attempts)
```

---

## Retry and Backoff

When a job fails:

- Attempt counter is incremented
- Next execution time is calculated using exponential backoff
- Job is returned to the queue
- Job is permanently marked FAILED after reaching the maximum retry count

Backoff schedule:

```text
Attempt 1 → 2 seconds
Attempt 2 → 4 seconds
Attempt 3 → 8 seconds
Attempt 4 → 16 seconds
```

---

## Basic Metrics

The worker records:

- Successful job executions
- Failed job executions

---

## Containerized Deployment

The application runs through Docker Compose and includes:

- PostgreSQL health checks
- Multi-container orchestration
- Environment-based configuration

---

## Project Structure

```text
distributed-job-scheduler
│
├── scheduler-service
│   ├── controller
│   ├── service
│   ├── repository
│   └── model
│
├── worker-service
│   ├── executor
│   ├── metrics
│   ├── poller
│   ├── repository
│   ├── service
│   └── model
│
├── docker-compose.yml
│
└── README.md
```

## Example Usage

### Submit a Job

```shell
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "payload":"example job"
  }'
```

### Check Job Status

```shell
curl http://localhost:8080/jobs/{jobId}
```

---

## Reliability Features

This project demonstrates several common distributed-system patterns:

- Persistent job queue
- State transitions
- Retry handling
- Exponential backoff
- Failure recovery
- Distributed worker architecture
- Structured logging
- Basic operational metrics

---

## Future Enhancements

Planned improvements include:

- Multiple worker instances
- Row-level locking for job claiming
- Cron scheduling
- Priority queues
- Dead-letter queue support
- Prometheus and Grafana integration
- Distributed tracing
- Kubernetes deployment

---

## Author

David Fifer

- LinkedIn: https://www.linkedin.com/in/david-b-fifer
- GitHub: https://github.com/davidfifer

---

## License

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Licensed under the MIT License. See [LICENSE](LICENSE) for full terms.
