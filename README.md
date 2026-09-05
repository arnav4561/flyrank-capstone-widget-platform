# FlyRank Capstone — Embeddable Widget & Lead-Capture Platform

A backend platform that allows customers to create embeddable widgets and safely collect submissions from external websites.

The project is built as a local-first capstone using FastAPI, PostgreSQL, Supabase Auth, Inngest, and a plain JavaScript embeddable widget.

## Project Status

Completed capstone implementation.

The implementation covers:

- authenticated widget management
- tenant isolation
- public widget configuration delivery
- versioned JavaScript widget delivery
- cross-origin rendering and submission
- payload validation and size limits
- rate limiting
- honeypot spam protection
- IP-based geo enrichment with provider fallback
- idempotent submissions
- PostgreSQL persistence
- dashboard APIs
- asynchronous side effects through Inngest
- retries and failure handling
- deterministic seed data
- automated tests
- second-origin browser demonstration

---

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker Compose
- Supabase Auth
- Inngest
- Plain JavaScript
- pytest

---

## Architecture

The application follows a layered backend structure:

```text
HTTP/API layer
    ↓
Service layer
    ↓
Repository layer
    ↓
PostgreSQL

Supporting infrastructure:

Supabase Auth
     ↓
FastAPI authentication dependency
     ↓
Tenant resolution
     ↓
Tenant-scoped repositories/services

Public widget flow:

Customer Website
      │
      │ <script>
      ▼
/widget/v1/widget.js
      │
      ▼
GET /api/v1/public/widgets/{public_id}
      │
      ▼
Render widget
      │
      │ POST submission
      ▼
Submission API
      │
      ├── payload validation
      ├── rate limiting
      ├── honeypot check
      ├── widget field validation
      ├── idempotency check
      ├── geo provider A
      │      └── fallback → provider B
      ├── PostgreSQL persistence
      └── Inngest side effect
Repository Structure
flyrank-capstone-widget-platform/
│
├── app/
│   ├── api/
│   │   ├── dashboard.py
│   │   ├── dependencies.py
│   │   ├── public_submissions.py
│   │   ├── public_widgets.py
│   │   ├── tenant.py
│   │   └── widgets.py
│   │
│   ├── core/
│   │   ├── database.py
│   │   ├── inngest.py
│   │   ├── rate_limit.py
│   │   └── supabase.py
│   │
│   ├── jobs/
│   │   └── submission.py
│   │
│   ├── models/
│   │   ├── submission.py
│   │   ├── tenant.py
│   │   └── widget.py
│   │
│   ├── repositories/
│   │   ├── dashboard.py
│   │   ├── submission.py
│   │   └── widget.py
│   │
│   ├── schemas/
│   │   ├── dashboard.py
│   │   ├── public_widget.py
│   │   ├── submission.py
│   │   └── widget.py
│   │
│   ├── services/
│   │   ├── dashboard.py
│   │   ├── geo.py
│   │   ├── submission.py
│   │   └── widget.py
│   │
│   ├── static/
│   │   └── widget.js
│   │
│   ├── main.py
│   └── seed.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── demo/
│   └── index.html
│
├── tests/
│
├── .env.example
├── .gitignore
├── BUILDLOG.md
├── DESIGN.md
├── EVIDENCE.md
├── capstone.yaml
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── README.md
Local Setup
Prerequisites

Install:

Python 3.11+
Docker Desktop
Git
Node.js/npm for the local Inngest Dev Server

A Supabase project is also required for authentication.

1. Clone the Repository
git clone https://github.com/arnav4561/flyrank-capstone-widget-platform.git
cd flyrank-capstone-widget-platform
2. Create a Python Virtual Environment

Windows PowerShell:

python -m venv venv
.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt
3. Configure Environment Variables

Copy .env.example to .env.

Windows PowerShell:

Copy-Item .env.example .env

Configure:

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/widget_platform
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-publishable-key
GEO_MOCK_MODE=true
INNGEST_DEV=1
INNGEST_EVENT_KEY=

Never commit .env.

The repository contains .env.example, while .env is ignored by Git.

Start PostgreSQL

Start the database:

docker compose up -d db

Check database readiness:

docker compose exec db pg_isready -U postgres -d widget_platform
Run Database Migrations
alembic upgrade head
Seed Demo Data
python -m app.seed

The seed command is idempotent.

Running it multiple times does not create duplicate demo tenants or widgets.

Start FastAPI
uvicorn app.main:app --reload

The API is available at:

http://localhost:8000

Health check:

GET /health

Database health check:

GET /health/db
Start Inngest Dev Server

In another terminal:

npx inngest-cli@latest dev

The Inngest development dashboard is normally available at:

http://localhost:8288

The FastAPI application exposes the Inngest endpoint at:

/api/inngest
API Endpoints
Authentication
GET /api/v1/auth/me

Requires:

Authorization: Bearer <Supabase access token>
Tenant
GET /api/v1/tenant/me

Requires authentication.

Widget Management
POST   /api/v1/widgets
GET    /api/v1/widgets
GET    /api/v1/widgets/{widget_id}
PATCH  /api/v1/widgets/{widget_id}
DELETE /api/v1/widgets/{widget_id}

All widget-management endpoints require authentication.

Widget records are scoped to the authenticated tenant.

Public Widget Configuration
GET /api/v1/public/widgets/{public_id}

No authentication is required.

The endpoint returns the public widget configuration and uses:

Cache-Control: public, max-age=60
Public Submission
POST /api/v1/public/widgets/{public_id}/submissions

The endpoint supports cross-origin requests and handles:

JSON validation
payload size limits
widget field validation
required fields
email validation
unexpected fields
honeypot spam detection
rate limiting
idempotency keys
IP capture
geo enrichment
asynchronous side effects
Dashboard
GET /api/v1/dashboard/widgets
GET /api/v1/dashboard/widgets/{widget_id}/submissions
GET /api/v1/dashboard/widgets/{widget_id}/stats

Dashboard endpoints require authentication and verify that the requested widget belongs to the authenticated tenant.

Embedding the Widget

A customer website can embed a widget with a single script:

<script
    src="http://127.0.0.1:8000/widget/v1/widget.js"
    data-widget="YOUR_PUBLIC_WIDGET_ID"
></script>

The JavaScript bundle:

reads the widget public ID
fetches the public configuration
renders the widget
collects visitor input
submits data to the public API
generates an idempotency key
displays success/error status

The bundle is served from:

/widget/v1/widget.js

The versioned URL is intended to allow future bundle versions without breaking existing embeds.

Cross-Origin Demo

The repository contains:

demo/index.html

Run the demo server:

python -m http.server 5500 --directory demo

Open:

http://127.0.0.1:5500

The demo page runs on port 5500, while the FastAPI API runs on port 8000.

Therefore they have different origins and exercise the real browser CORS path.

The page loads the widget using:

<script
    src="http://127.0.0.1:8000/widget/v1/widget.js"
    data-widget="YOUR_PUBLIC_WIDGET_ID"
    data-container="flyrank-widget"
></script>
Submission Security Controls
Payload Size

Requests larger than 16 KB are rejected with:

413 Request payload too large

Malformed JSON returns a JSON 4xx response rather than a server error.

Field Validation

The server validates submitted fields against the widget configuration.

It checks:

required fields
supported field names
text values
email values
unexpected fields

Invalid submissions return 422.

Rate Limiting

The local implementation permits up to five submissions per IP address within a 60-second window.

Exceeding the limit returns:

429 Too Many Requests

The current limiter is intentionally in-memory and is suitable for the local/single-process capstone implementation.

Honeypot

The widget contains a hidden website field.

If the field is populated, the submission is rejected.

This provides a simple bot/spam detection mechanism without requiring an external CAPTCHA service.

Geo Enrichment

The submission pipeline attempts:

Provider A: ip-api.com
       ↓ failure
Provider B: ipapi.co
       ↓ failure
Store submission without geo data

For deterministic capstone testing, GEO_MOCK_MODE=true provides predictable provider outcomes.

Test IPs:

203.0.113.10 → Provider A succeeds

203.0.113.20 → Provider A fails, Provider B succeeds

203.0.113.30 → both providers fail, submission still stores
Idempotency

The submission API accepts:

Idempotency-Key

The key is scoped to:

tenant + widget + idempotency key

A database unique index prevents duplicate records for the same idempotency key.

Background Side Effects

After a successful submission is stored, the API sends an Inngest event:

widget/submission.created

The background function processes the side effect asynchronously.

The function is configured with retries.

A side-effect failure therefore does not cause the already-successful submission API request to become a failure.

The implementation also logs a failure alert when side-effect processing ultimately fails.

Testing

Run:

pytest -v

The automated suite covers:

submission validation
required fields
unexpected fields
email validation
text validation
geo Provider A success
geo Provider A → Provider B fallback
both geo providers failing
invalid IP handling
rate limiting
rate-limit window reset

Manual evidence additionally covers:

authenticated widget CRUD
public widget delivery
cache headers
cross-origin browser rendering
CORS preflight
real PostgreSQL persistence
Inngest event processing
Inngest retry/failure behavior
idempotent seed execution
Database

PostgreSQL is run locally through Docker Compose.

Database schema changes are managed with Alembic migrations.

Current core tables:

tenants
widgets
submissions

Important indexes include:

tenant ownership
widget public ID
submission tenant/widget relationships
submission creation time
submission idempotency key
Multi-Tenant Isolation

The authenticated user is resolved through Supabase Auth.

The application maps the Supabase user ID to an internal tenant.

Authenticated widget and dashboard queries always include the current tenant ID.

Therefore a tenant cannot access another tenant's widget or submission records through the application APIs.

Design Documentation

See:

DESIGN.md

for:

data model
tenancy model
API contracts
widget lifecycle
submission flow
indexes
embed architecture
non-goals
Evidence

See:

EVIDENCE.md

for requirement-by-requirement proof and manual test evidence.

Development Log

See:

BUILDLOG.md

for the implementation history and AI-assisted development record.

Capstone Manifest

See:

capstone.yaml

for the evaluator-oriented run, seed, test, base URL, and endpoint information.

Known Local Limitations

This capstone intentionally remains local-first.

The current implementation does not attempt production-scale infrastructure such as:

distributed rate limiting
horizontally scaled workers
production CDN deployment
managed production PostgreSQL
production email delivery
production webhook delivery
advanced bot detection

The in-memory rate limiter is therefore a deliberate capstone simplification.

License

This project is provided for the FlyRank internship capstone.