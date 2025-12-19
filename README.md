# testDM FastAPI Bootstrap

Minimal bootstrap for a **FastAPI** application.

A single route is exposed as an example: `/health`.

---

## Tech stack

- Python 3.11+
- FastAPI
- Pydantic v2
- pydantic-settings
- pytest / pytest-asyncio
- pytest-cov
- httpx

---

## Architecture (logical view)

The project follows a **lightweight hexagonal (clean) architecture**.

- **FastAPI** acts as an HTTP adapter  
- The **domain** is independent from the framework and the infrastructure  
- **Configuration** is centralized and injected  
- Infrastructure (DB, external services) will be added later  

Some packages are intentionally empty at this stage and will be populated as features are added.

### Diagram

```
                ┌─────────────────────┐
                │     FastAPI API     │
                │  (routes, schemas)  │
                └─────────▲───────────┘
                          │
                          │ HTTP mapping / Depends
                          │
                ┌─────────┴───────────┐
                │     Services        │
                │   (business logic)  │
                └─────────▲───────────┘
                          │
                     dependencies
                          │
                ┌─────────┴───────────┐
                │        Ports        │
                │ (abstract contracts)│
                └─────────▲───────────┘
                          │
                   implementations
                          │
                ┌─────────┴───────────┐
                │   Infrastructure    │
                │ (DB, APIs, etc.)    │
                └─────────────────────┘
```

### Key rules

- Dependencies always point **towards the domain**
- The domain knows nothing about FastAPI, configuration, or the database
- Infrastructure is interchangeable
- The bootstrap contains **no concrete data access implementation**

---

## Configuration / Settings

Configuration is centralized in a `settings` module based on
**pydantic-settings**.

Principles:
- values are read from **environment variables**
- optional support for a local `.env` file
- the domain has no dependency on configuration

### `.env` example (local)

```env
APP_NAME=Senior FastAPI Bootstrap
ENV=dev
DEBUG=true
SECRET_KEY=change-me
```

> In production, environment variables are provided by the execution
> environment (Docker, Cloud Run, CI/CD, etc.).

---

## Installation

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

---

## Running the API

```bash
uvicorn app.main:app --reload
```

FastAPI applications are ASGI applications and must be executed by an
ASGI server.  
**Uvicorn** is used here as the ASGI runtime responsible for handling
network connections and the event loop.

Available route:

- `GET /health`

---

## Tests

Run the test suite:

```bash
pytest
```

Tests cover:
- the API layer
- the application bootstrap

---

## Code coverage

Code coverage is configured automatically via `pytest-cov`.

```bash
pytest
```

Coverage report is displayed in the console.

HTML report:

```bash
pytest --cov-report=html
open htmlcov/index.html
```
