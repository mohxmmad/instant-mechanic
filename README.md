# Instant Mechanic — Django REST API

Production-quality backend for a mechanic-service platform. Provides JWT-authenticated CRUD for mechanics and service-request management with PostgreSQL, Docker, OpenAPI/Swagger, pagination/search/filter/ordering, logging, health checks, seed data, and automated tests.

## Features

**Required**
- Mechanic CRUD: `GET/POST /api/v1/mechanics/`, `GET/PUT/PATCH/DELETE /api/v1/mechanics/{id}/`
- Service Requests: `POST/GET /api/v1/service-requests/`, `GET/PATCH/PUT/DELETE /api/v1/service-requests/{id}/` (status transitions enforced)
- ForeignKey `mechanic` relationship, default `PENDING` status
- Validation: phone, vehicle number, required fields, nonexistent mechanic, invalid service/rating/status, duplicate handling
- Proper error JSON + HTTP codes (200/201/204/400/401/404/500), no tracebacks

**Bonus (all implemented)**
- JWT authentication (`/api/v1/auth/register|login|refresh/`)
- Pagination (10/page), search (`?search=rahul`), filtering (`?location=Gurgaon&is_open=true`), ordering (`?ordering=-rating`)
- Swagger/OpenAPI at `/api/docs/` + `/api/schema/` (drf-spectacular)
- Unit tests (33) runnable inside Docker
- Docker + Docker Compose (PostgreSQL 16-alpine)
- PostgreSQL with indexes/constraints
- Clean architecture: URL → ViewSet → Serializer → Model → ORM
- Logging (INFO/WARNING/ERROR, no secrets/PII)
- Health check `/api/v1/health/` with DB probe
- Seed data via `python manage.py seed_data`
- Admin with list_display/filters/search
- `config/settings/{base,local,production}.py` separation + env vars
- Gunicorn + WhiteNoise for production

## Tech Stack

- Python 3.12, Django 5.1.8
- Django REST Framework 3.15.2, django-filter 25.1
- PostgreSQL 16 (psycopg2-binary 2.9.10)
- djangorestframework-simplejwt 5.3.1 (JWT)
- drf-spectacular 0.28.0 (OpenAPI 3.0)
- Gunicorn 23, WhiteNoise 6.8
- Docker / Docker Compose, Render Postgres (prod DB), Render (prod host via Blueprint)

## Architecture

```
Client (Swagger / curl)
  ↓
Django REST Framework (JWT auth, IsAuthenticated, pagination, filters)
  ↓
ViewSet (apps/mechanics, service_requests, accounts, core)
  ↓
Serializer (validation, status transitions)
  ↓
Django ORM / Model (Mechanic, ServiceRequest, User)
  ↓
PostgreSQL
```

Logging via `apps.core.exceptions.custom_exception_handler` (logs 4xx/5xx, hides tracebacks).

## Project Structure

```
.
├── apps/
│   ├── accounts/          # User model, register/login/refresh, JWT
│   │   ├── models.py      # Custom User (AbstractUser, email unique)
│   │   ├── serializers.py # Register/Login validation
│   │   └── tests.py       # Auth tests
│   ├── mechanics/         # Mechanic model/ViewSet/Serializer
│   │   ├── models.py      # indexes on name/location/rating/is_open
│   │   └── tests.py       # CRUD/search/filter/pagination
│   ├── service_requests/  # ServiceRequest FK → Mechanic
│   │   ├── models.py      # status choices, indexes
│   │   └── tests.py       # creation, validation, transitions
│   └── core/              # health, exceptions, seed_data command
│       ├── views.py       # GET /api/v1/health/
│       └── management/commands/seed_data.py
├── config/
│   ├── settings/
│   │   ├── base.py        # shared apps/middleware/DRF/JWT/Spectacular/logging/DB
│   │   ├── local.py       # DEBUG=True, ALLOWED_HOSTS=*
│   │   └── production.py  # DEBUG=False, HSTS, secure cookies, SSL
│   ├── urls.py            # /api/v1/*, /api/docs/, /api/schema/, /admin/
│   └── wsgi.py / asgi.py
├── Dockerfile             # python:3.12-slim, gunicorn, collectstatic
├── docker-compose.yml     # web (Django) + db (Postgres), healthcheck
├── requirements.txt
├── .env.example
├── .dockerignore / .gitignore
└── manage.py
```

## Local Setup

```bash
git clone <repo>
cd instant-mechanic
cp .env.example .env
# edit .env if needed — POSTGRES_HOST must be `db` (service name, not localhost)

docker compose up --build
```

This builds the image, starts PostgreSQL, runs migrations automatically (web command: `migrate && runserver`), and serves at `http://localhost:8000`.

*Migrations run on container start. To run manually:*

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Verify:

```bash
curl http://localhost:8000/api/v1/health/
# {"status":"healthy","database":"connected"}

open http://localhost:8000/api/docs/   # Swagger UI
open http://localhost:8000/api/schema/ # Raw OpenAPI YAML/JSON
open http://localhost:8000/admin/      # Django Admin
```

## Seed Data

```bash
docker compose exec web python manage.py seed_data
# Clears? No. To reset:
docker compose exec web python manage.py seed_data --clear
```

Creates demo user `demo / demo12345`, 10 mechanics (Gurgaon/Delhi/Noida/Faridabad, varied ratings/services/open status), 20 service requests with random statuses and dates (last 30 days). Uses `--clear` to wipe existing mechanics/service-requests first.

Local host equivalent (without Docker, needs Postgres reachable at POSTGRES_HOST):

```bash
python manage.py seed_data
```

## API Documentation

- Swagger UI: `http://localhost:8000/api/docs/`
- Schema: `http://localhost:8000/api/schema/` (OpenAPI 3.0)

Click **Authorize** (padlock) → `Bearer <access_token>` to test authenticated endpoints from Swagger. All mechanic/service-request endpoints require JWT except `health` and `auth/*`.

## Authentication

JWT via `djangorestframework-simplejwt` (access 30m, refresh 7d, `Bearer` header).

**Public:** `POST /api/v1/auth/register|login|refresh/`, `GET /api/v1/health/`, `GET /api/schema/`, `GET /api/docs/`

**Protected (IsAuthenticated):** `mechanics/*`, `service-requests/*`

Flow:

1. `POST /api/v1/auth/register/` → `{access, refresh}`
2. `POST /api/v1/auth/login/` → `{access, refresh}`
3. Use `Authorization: Bearer <access>` on subsequent calls
4. `POST /api/v1/auth/refresh/` with `{"refresh": "<refresh>"}` → new `access`

Passwords are hashed via Django's PBKDF2; never logged.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register/` | No | Register `{username,email,password}` → 201 + tokens |
| POST | `/api/v1/auth/login/` | No | Login `{username,password}` (username or email) → tokens |
| POST | `/api/v1/auth/refresh/` | No | Refresh `{"refresh": "..."}` → new access |
| GET | `/api/v1/health/` | No | DB probe → `{status, database}` |
| GET | `/api/v1/mechanics/` | Yes | List (paginated, searchable, filterable, orderable) |
| POST | `/api/v1/mechanics/` | Yes | Create |
| GET | `/api/v1/mechanics/{id}/` | Yes | Retrieve |
| PUT | `/api/v1/mechanics/{id}/` | Yes | Full update |
| PATCH | `/api/v1/mechanics/{id}/` | Yes | Partial update |
| DELETE | `/api/v1/mechanics/{id}/` | Yes | Delete (204) |
| GET | `/api/v1/service-requests/` | Yes | List |
| POST | `/api/v1/service-requests/` | Yes | Create (default PENDING) |
| GET | `/api/v1/service-requests/{id}/` | Yes | Retrieve |
| PATCH | `/api/v1/service-requests/{id}/` | Yes | Status transition (PENDING→IN_PROGRESS/CANCELLED, etc.) |
| PUT | `/api/v1/service-requests/{id}/` | Yes | Full update |
| DELETE | `/api/v1/service-requests/{id}/` | Yes | Delete |
| GET | `/api/schema/` | No | OpenAPI schema |
| GET | `/api/docs/` | No | Swagger UI |

Query params for mechanics:

```
/api/v1/mechanics/?search=rahul
/api/v1/mechanics/?location=Gurgaon&is_open=true
/api/v1/mechanics/?ordering=-rating
/api/v1/mechanics/?page=2
```

## Example Requests / Responses

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"StrongPass123!"}'
# 201
# {"id":1,"username":"alice","email":"alice@example.com","access":"eyJ...","refresh":"eyJ..."}

curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"StrongPass123!"}'
# 200
# {"access":"eyJ...","refresh":"eyJ..."}
```

### Create mechanic

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"StrongPass123!"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

curl -X POST http://localhost:8000/api/v1/mechanics/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Rahul Sharma","phone":"+919876543210","location":"Gurgaon","rating":4.5,"is_open":true,"services":["engine repair","oil change"]}'
# 201
# {"id":1,"name":"Rahul Sharma","phone":"+919876543210","location":"Gurgaon","rating":"4.50","is_open":true,"services":["engine repair","oil change"],"created_at":"...","updated_at":"..."}
```

### List mechanics (paginated)

```bash
curl http://localhost:8000/api/v1/mechanics/ -H "Authorization: Bearer $TOKEN"
# 200
# {"count":1,"next":null,"previous":null,"results":[{...}]}
```

### Create service request

```bash
curl -X POST http://localhost:8000/api/v1/service-requests/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Arjun Mehra","customer_phone":"9876543210","vehicle_number":"MH01AB1234","mechanic":1,"service":"engine repair","problem_description":"Engine noise"}'
# 201
# {"id":1,"customer_name":"Arjun Mehra","customer_phone":"9876543210","vehicle_number":"MH01AB1234","mechanic":1,"service":"engine repair","problem_description":"Engine noise","status":"PENDING","created_at":"...","updated_at":"..."}
```

Validation errors return 400 with field map, e.g. `{"phone":["Invalid phone number..."]}`; auth failure 401; not found 404.

## Testing

Tests use Django's `TestCase` + DRF `APITestCase` (33 tests covering auth, mechanics, service-requests, health).

Run inside Docker (required — uses the Compose Postgres):

```bash
docker compose exec web python manage.py test --verbosity=1
# Or rebuild first:
docker compose up --build -d
docker exec instant-mechanic-web-1 python manage.py test --verbosity=1
```

Run locally (host must reach Postgres; set `POSTGRES_HOST=localhost` in `.env`):

```bash
POSTGRES_HOST=localhost python manage.py test --verbosity=1
```

Covered:

- Auth: register, duplicate username, login success/email, invalid creds, protected access, refresh
- Mechanics: create, retrieve, PUT, PATCH, DELETE, invalid ID, phone/rating/required validation, search, filter, ordering, pagination
- Service Requests: creation (PENDING), FK relationship, nonexistent/invalid mechanic, missing fields, blank service, invalid phone/vehicle, list/retrieve, invalid/valid status transitions, auth guard

## Production

**Architecture:** `User → Render Web Service (Gunicorn) → Render Postgres` — local Docker Postgres (`docker-compose.yml:2` `db`) is dev-only; prod uses a managed Render Postgres. The app reads `DATABASE_URL` from env (`config/settings/base.py:64`), so you can point it at any Postgres by changing the env var.

**Deploy as Web Service + Database (manual combo):**

1. **Create database:** Render Dashboard → **New → PostgreSQL** → name `instant-mechanic-db` → region `Oregon` (or nearest) → **Create**. Wait for `Available`, then copy its **Internal Connection String** (preferred) — e.g., `postgres://user:pass@dpg-xxx.oregon-postgres.render.com/db`. Use **External Connection String** only if connecting from outside Render.

2. **Create web service:** **New → Web Service** → connect `mohxmmad/instant-mechanic` repo → branch `prod` → **Runtime: Docker** (uses `Dockerfile:1`) → **Add Environment Variables:**
   ```
   DJANGO_SETTINGS_MODULE=config.settings.production
   SECRET_KEY=<generate 50+ random chars>
   DATABASE_URL=<paste Internal Connection String from step 1>   # <-- choose your DB URL here
   ALLOWED_HOSTS=<your-service>.onrender.com
   # optional: POSTGRES_DB/USER/PASSWORD/HOST/PORT also work if you prefer individual vars over DATABASE_URL
   ```
   No code change needed — `base.py:64` `_get_database_config()` checks `DATABASE_URL` first, then falls back to `POSTGRES_*`. To switch databases later, just update `DATABASE_URL` in Render → **Environment** → **Save** → redeploy.

3. **Build & start:** Build runs `Dockerfile:17` `collectstatic`; start runs `Dockerfile:21` `python manage.py migrate --noinput && gunicorn ... --bind 0.0.0.0:${PORT:-8000}`. Migrations run on every start; health check at `/api/v1/health/` (`apps/core/views.py:14`) must return `200`.

4. **Blueprint alternative:** Repo includes `render.yaml:1` (web + db). For one-click provisioning: **New → Blueprint** → connect repo → branch `prod` → **Apply**. Then override `DATABASE_URL` in the web service if you want to point at a different DB.

5. **Verify:** `curl https://<your-service>.onrender.com/api/v1/health/` → `{"status":"healthy","database":"connected"}`. Swagger at `/api/docs/` should show `Mechanic`/`ServiceRequest` (not `ServiceRequestRequest` via `COMPONENT_SPLIT_REQUEST=False`).

`docker-compose.yml:7` still uses `POSTGRES_HOST=db` for local; prod uses `DATABASE_URL` — same image works in both envs.

**Static:** WhiteNoise serves `staticfiles/` (collected at build). `production.py` enforces `DEBUG=False`.

**Superuser & seed on startup (no shell needed):** Image start runs `apps/core/management/commands/init_prod.py:1` after `migrate` (`Dockerfile:21` + `docker-compose.yml:21`):
- Creates/updates superuser `admin` / `admin@gmail.com` / `admin` (use for `https://.../admin/`)
- If no `Mechanic` exists, runs `seed_data` (10 mechanics + 20 requests + demo user). Redeploy on Render or `docker compose up --build` auto-seeds — no manual `createsuperuser` or `seed_data` required. To reset demo data: `docker compose exec web python manage.py seed_data --clear`.

**Migrations / Admin:** Manual fallback still works: `docker compose exec web python manage.py migrate && python manage.py createsuperuser` (local) or Render Shell (prod). Admin at `/admin/` with `Mechanic`/`ServiceRequest`/`User` list displays — login with `admin`/`admin` after first boot.

## License

For internship evaluation only.
