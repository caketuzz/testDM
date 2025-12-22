![CI](https://github.com/caketuzz/testDM/actions/workflows/deploy.yml/badge.svg)

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

The email service is treated as a third-party dependency and mocked through dependency injection.
Sending emails is not part of the exercise scope.

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

### Security
Security considerations

Several security concerns are addressed explicitly:

#### Activation code verification

Codes are compared using constant-time comparison to mitigate timing attacks

Activation codes are:

time-limited

attempt-limited

invalidated after successful use

#### Brute-force protection

A bounded number of attempts is enforced per activation code

Attempt counters are stored server-side

Lockout logic is handled at the domain level

#### User enumeration protection

API responses do not reveal whether:

the email exists

the activation code is invalid

the activation code is expired

All failure cases return neutral responses.
Detailed causes are logged internally for observability.

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

## Run the app

First, create the `.env` file:

```bash
cp .env.example .env
```

### Run in dev mode (hot reload + volume mount)

```bash
docker compose --profile dev up --build
```

- Mounts the source code from your machine
- Enables hot reload
- Uses the `dev` Docker target
- Relies on `.env` or shell env

### Run in prod mode (self-contained image)

```bash
docker compose --profile prod up --build
```

- Builds a full Docker image with app code
- No code volume
- Closer to deployment setup

---

## Run tests

```bash
docker compose run --rm api pytest
```

---

## Code coverage

```bash
docker compose run --rm api pytest --cov
```

To view HTML coverage report:

```bash
docker compose run --rm api pytest --cov-report=html
open htmlcov/index.html
```

## Notes

- The API will still boot if the database is unavailable (health check shows DB: KO)
- Logs are managed using FastAPI’s internal logger
- Secret keys and sensitive variables should **not** be committed. Example files are provided and overrides should be environment-specific
