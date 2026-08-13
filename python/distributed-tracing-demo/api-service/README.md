# API Service

A lightweight FastAPI application packaged in a Docker container and served using Uvicorn. The service exposes an API
defined in `src/main.py` and runs on port 8000. It includes a simple health‑check endpoint that returns a basic status
message, making it easy to confirm the service is up and running.

---

## Overview

The API Service is a minimal FastAPI application intended for use in containerized environments or as a foundational
building block for larger systems. It provides a straightforward example of how to structure a FastAPI project, package
it with Docker, and run it using Uvicorn.

This service is intentionally simple—ideal for demos, scaffolding new microservices, or validating infrastructure setups.

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
- Simple health‑check endpoint

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
- Port 8000 available
- Python 3.11 (optional, for running locally without Docker)

---

## Running with Docker

### Build the Image

```bash
docker build -t api-service .
```

### Run the Container

```bash
docker run -d -p 8000:8000 api-service
```

### Accessing the Service

Once running, access the root endpoint:

```text
http://localhost:8000
```

The service will respond with a simple health‑check message confirming it is up and running.

---

## Dockerfile Overview

This service uses a simple Dockerfile that:

- Sets the working directory
- Installs dependencies from `requirements.txt`
- Copies the application source
- Starts Uvicorn on `0.0.0.0:8000`

---

## Contributing

To contribute to the development of api-service:

1. Fork api-service from https://github.com/davidfifer/davidfifer-portfolio/fork
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

### 0.0.1
- Initial working version

---

## License

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Licensed under the MIT License. See [LICENSE](LICENSE) for full terms.
