# ShipEngine Address Validation Service

Async CRUD service for address validation using ShipEngine API (mock).

## Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy 2.x** - ORM (async)
- **PostgreSQL** - Database (asyncpg driver)
- **ARQ** - Background tasks
- **Redis** - Task queue
- **Pydantic v2** - Validation
- **Alembic** - Migrations

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd shipengine-address-service
cp .env.example .env

# Start services
docker compose up -d

# Run migrations
docker compose exec app alembic upgrade head

# API docs
open http://localhost:8000/docs
```

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run locally (requires DB and Redis)
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest

# Lint & format
uv run ruff check src tests
uv run ruff format src tests
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `DEBUG` | Enable debug mode | `false` |
| `SHIPENGINE_API_KEY` | ShipEngine API key (mock) | - |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/addresses` | Create address + enqueue validation |
| GET | `/api/v1/addresses` | List addresses (paginated) |
| GET | `/api/v1/addresses/{id}` | Get address with validation results |
| PUT | `/api/v1/addresses/{id}` | Update address + re-validate |
| DELETE | `/api/v1/addresses/{id}` | Delete address |
| POST | `/api/v1/addresses/{id}/validate` | Trigger re-validation |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/health/ready` | Readiness check |

## Architecture

```
Request → FastAPI → Service → Repository → Database
                      ↓
                   ARQ Queue → Worker → ShipEngine API (mock)
```

### Flow

1. Client creates address via POST `/api/v1/addresses`
2. Address saved with `validation_status=PENDING`
3. Background task enqueued to ARQ
4. Worker validates address via ShipEngine (mock)
5. Validation result saved, address status updated
6. Client polls GET `/api/v1/addresses/{id}` for status

## Project Structure

```
src/
├── main.py           # FastAPI app + lifespan
├── config.py         # Pydantic settings
├── core/
│   ├── exceptions.py # Domain exceptions
│   └── enums.py      # ValidationStatus enum
├── db/
│   ├── models/       # SQLAlchemy models
│   └── session.py    # Async session factory
├── api/
│   ├── dependencies/ # DI: get_db, get_service
│   └── routes/       # API endpoints
├── schemas/          # Pydantic request/response
├── repositories/     # Generic + Address repo
├── services/         # Business logic
└── workers/          # ARQ tasks + settings

tests/
├── conftest.py       # Shared fixtures
├── constants.py      # Test constants
├── factories/        # Polyfactory models
├── unit/             # Unit tests (mocked)
└── integration/      # API tests (SQLite)
```

## Docker

```bash
# Build and run all services
docker compose up --build

# View logs
docker compose logs -f app worker

# Run migrations
docker compose exec app alembic upgrade head

# Stop
docker compose down
```

## Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=term-missing

# Unit only
uv run pytest tests/unit -v

# Integration only
uv run pytest tests/integration -v
```
