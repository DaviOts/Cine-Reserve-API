# CineReserve API

A production-ready cinema reservation API built with Django REST Framework, featuring distributed seat locking via Redis, asynchronous task processing with Celery, JWT authentication, and automated CI/CD.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Features](#features)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [CI/CD](#cicd)
- [Design Decisions](#some-design-decisions-that-ive-made)

---

## Overview

CineReserve is a RESTful API for managing cinema sessions, seat reservations, and ticket purchases. It handles concurrent reservation attempts safely using distributed Redis locks, prevents seat double-booking with PostgreSQL row-level locking (`SELECT FOR UPDATE`), and sends ticket confirmation emails asynchronously via Celery.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 6.0 + Django REST Framework 3.17 |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Task Queue | Celery 5.6 + Celery Beat |
| Auth | JWT via `djangorestframework-simplejwt` |
| API Docs | Swagger UI via `drf-spectacular` |
| Rate Limiting | `django-ratelimit` |
| Containerization | Docker + Docker Compose |
| Testing | pytest + pytest-django + model-bakery |
| Linting | Ruff |
| CI/CD | GitHub Actions |

---

## Architecture

```
apps/
├── users/          # JWT auth — register, login, token refresh
├── movies/         # Movies + Sessions CRUD (ViewSet + Router)
├── seats/          # Seat map per session (ListAPIView)
├── reservations/   # Distributed Redis lock (APIView)
└── tickets/        # Checkout + My Tickets + email notification

config/             # settings, urls, celery
utils/              # custom exception handler (429)
tests/              # conftest.py + per-app test directories
```

### Redis Usage (3 distinct purposes)

```
1. Seat Lock       →  SET seat_lock:{seat_id} {user_id} EX 600 NX
2. Django Cache    →  movies:list, sessions:list, movies:retrieve, sessions:retrieve
3. Rate Limit      →  django-ratelimit counters per IP
```

---

## Features

### JWT Authentication
Register and login with email/password. Access tokens expire in 30 minutes; refresh tokens last 1 day.

```bash
POST /api/users/register/
POST /api/users/login/
POST /api/users/token/refresh/
```

---

### Movies & Sessions
Full CRUD for movies and sessions. Public read access, authenticated write access. Results are paginated (20 per page) and cached in Redis for 15 minutes.

---

### Seat Reservation with Distributed Locking

When a user reserves a seat, the API:
1. Acquires an atomic Redis lock (`SET ... NX EX 600`) — only one user can hold the lock
2. Marks the seat as `RESERVED` in the database
3. Returns `409 Conflict` with TTL if the seat is already locked by another user

On cancellation (DELETE), the lock is released and the seat reverts to `AVAILABLE`.

```bash
POST   /api/reservations/sessions/{session_id}/seats/{seat_id}/reserve/
DELETE /api/reservations/sessions/{session_id}/seats/{seat_id}/reserve/
```

The seat map endpoint reflects real-time lock state — available seats with an active Redis lock are shown as `reserved` (transient, not persisted):

```bash
GET /api/seats/sessions/{session_id}/seats/
```

---

### Ticket Purchase

Checkout uses `SELECT FOR UPDATE` to prevent race conditions at the database level. The flow:

1. Validates the Redis lock owner matches the requesting user
2. Acquires a PostgreSQL row-level lock on the seat
3. Marks seat as `PURCHASED` and creates the `Ticket` record with a SHA256 QR code
4. On `transaction.on_commit`: releases the Redis lock and triggers the email task

```bash
POST /api/tickets/purchase/
GET  /api/tickets/my-tickets/
```

---

### Email Confirmation via Celery

After a successful purchase, an email is sent asynchronously. The task is only dispatched after the database transaction commits (`transaction.on_commit`), preventing orphaned tasks.

**Console output (dev mode):**

```
Content-Type: text/plain; charset="utf-8"
Subject: Your Ticket
From: noreply@cinereserve.com
To: davi@example.com

Hey daviots, your ticket has been confirmed

Ticket ID: 3f2a1b4c-...

Let's go to the moviesss
```

> I used `EMAIL_BACKEND`(only for tests), but in production swap for SMTP (SendGrid, SES, etc.)

---

### Expired Lock Cleanup (Celery Beat)

A periodic task runs every 60 seconds and scans for seats with status `RESERVED` whose Redis lock has expired. These are reverted to `AVAILABLE` automatically, ensuring no seat stays permanently locked if a user abandons the reservation.

```python
# apps/reservations/tasks.py
@shared_task
def release_expired_seat_locks():
    reserved_seats = Seat.objects.filter(status=SeatStatus.RESERVED)
    for seat in reserved_seats:
        if not redis_client.exists(f"seat_lock:{seat.id}"):
            seat.status = SeatStatus.AVAILABLE
            seat.save()
```

---

### Rate Limiting

All endpoints are rate-limited by IP using `django-ratelimit`. Custom 429 handler returns a structured JSON response.

| Endpoint | Limit |
|---|---|
| `GET /movies`, `GET /sessions` | 60 req/min |
| `GET /seats` | 30 req/min |
| `POST /reserve` | 10 req/min |
| `POST /purchase` | 5 req/min |
| `POST /login` | 10 req/min |
| `POST /register` | 5 req/min |

```json
{ "error": "Too many requests. Please slow down." }
```

---

### Auto Seat Creation via Signal

When a `Session` is created, a `post_save` signal automatically generates all seats based on `total_seats`, distributed evenly across rows A–J using `bulk_create`.

```python
@receiver(post_save, sender=Session)
def create_seats_for_session(sender, instance, created, **kwargs):
    if not created:
        return
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    seats_per_row = instance.total_seats // len(rows)
    seats = [Seat(session=instance, row=row, number=n)
             for row in rows for n in range(1, seats_per_row + 1)]
    Seat.objects.bulk_create(seats)
```

---

### Swagger UI

Interactive API documentation available at:

```
GET /api/docs/
GET /api/schema/
```

---

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/DaviOts/Cine-Reserve-API
cd Cine-Reserve-API
```

### 2. Create the `.env` file

```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Start all services

```bash
docker compose up --build
```

This starts: `api`, `postgres`, `redis`, `celery` (worker), `celery_beat`.

The API will be available at `http://localhost:8000`.

### 4. Access the docs

```
http://localhost:8000/api/docs/
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Enable debug mode | `False` |
| `POSTGRES_DB` | Database name | `cinereserve_db` |
| `POSTGRES_USER` | Database user | `cinereserve_user` |
| `POSTGRES_PASSWORD` | Database password | — |
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6380/0` |

---

## API Endpoints

### Users
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/users/register/` | No | Register new user |
| POST | `/api/users/login/` | No | Login, returns JWT tokens |
| POST | `/api/users/token/refresh/` | No | Refresh access token |

### Movies & Sessions
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/catalog/movies/` | No | List all movies (cached) |
| POST | `/api/catalog/movies/` | Yes | Create movie |
| GET | `/api/catalog/movies/{id}/` | No | Retrieve movie (cached) |
| GET | `/api/catalog/sessions/` | No | List sessions, filter by `?movie_id=` |
| POST | `/api/catalog/sessions/` | Yes | Create session (triggers seat creation) |

### Seats
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/seats/sessions/{id}/seats/` | Yes | Seat map with live lock status |

### Reservations
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/reservations/sessions/{sid}/seats/{seat_id}/reserve/` | Yes | Reserve seat (Redis lock) |
| DELETE | `/api/reservations/sessions/{sid}/seats/{seat_id}/reserve/` | Yes | Release reservation |

### Tickets
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/tickets/purchase/` | Yes | Purchase ticket |
| GET | `/api/tickets/my-tickets/` | Yes | List current user's tickets |

---

## Running Tests

```bash
# All tests with verbose output
poetry run pytest tests/ -v

# Specific module
poetry run pytest tests/reservations/ -v

# With coverage
poetry run pytest tests/ --cov=apps --cov-report=term-missing
```

### Test Structure

```
tests/
├── conftest.py              # Global fixtures + autouse cache reset
├── test_ratelimit.py        # All rate limit tests centralized
├── movies/
│   ├── test_serializers.py
│   └── test_views.py
├── reservations/
│   ├── test_services.py
│   ├── test_tasks.py
│   └── test_views.py
├── seats/
│   ├── test_serializers.py
│   └── test_views.py
├── tickets/
│   ├── test_services.py
│   ├── test_tasks.py
│   └── test_views.py
└── users/
    ├── test_serializers.py
    └── test_views.py
```

Redis is always mocked in unit tests. Integration tests that use `transaction.on_commit` use `@pytest.mark.django_db(transaction=True)`.

---

## CI/CD

GitHub Actions pipeline runs on every push/PR to `main`:

1. **Services**: PostgreSQL 16 + Redis 7 with health checks
2. **Install**: Poetry + dependencies (cached)
3. **Lint**: `ruff check .`
4. **Test**: `pytest tests/ -v --tb=short`

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    services:
      postgres:
        image: postgres:16-alpine
      redis:
        image: redis:7-alpine
```

---

## Some Design Decisions that i`ve made

### Why Redis for seat locking instead of just the database?

A database lock (`SELECT FOR UPDATE`) only works within a transaction — it's released the moment the transaction ends. A reservation needs to persist for up to 10 minutes while the user completes checkout. Redis `SET NX EX` provides a distributed, TTL-aware lock that survives across requests and multiple API instances.

### Why `transaction.on_commit` for Celery tasks?

If the email task were dispatched inside the transaction, it could execute before the database commits — the worker would try to fetch a ticket that doesn't exist yet. `on_commit` guarantees the task only runs after the transaction is fully persisted.

### Why manual cache inside the view instead of `cache_page`?

`cache_page` wraps the entire request/response cycle and intercepts the request before Django processes it — this means `django-ratelimit` never gets a chance to count the request. Manual `cache.get/set` inside the view runs after the ratelimit decorator, preserving correct rate limiting behavior.

### Why persist `RESERVED` status on the database?

The Celery Beat task (`release_expired_seat_locks`) queries `Seat.objects.filter(status=RESERVED)` to find seats whose Redis lock has expired. Without persisting `RESERVED` to the database, this query always returns zero results and the cleanup task never runs.

<h4 align="center">Made By Otavszin א♥</h4>
<p align="center">
  <a href="https://github.com/DaviOts">github.com/DaviOts</a>
</p>