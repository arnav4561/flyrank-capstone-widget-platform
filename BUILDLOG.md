# FlyRank Capstone — Build Log

This document records the development progress, implementation decisions, testing, and AI-assisted development used during the FlyRank Backend Track capstone.

---

## Project

**FlyRank Internship · Backend Track · Capstone**

**Project:** Embeddable Widget & Lead-Capture Platform

**Repository:**

https://github.com/arnav4561/flyrank-capstone-widget-platform

---

# Development Approach

The project was developed incrementally in stages.

The main workflow was:

1. design the architecture
2. initialize the repository
3. configure the development environment
4. implement persistence
5. implement authentication and tenancy
6. implement widget CRUD
7. implement public widget delivery
8. implement submission handling
9. harden the submission pipeline
10. add geo fallback
11. add asynchronous side effects
12. add dashboard APIs
13. add automated tests
14. add a second-origin demo
15. document and verify the capstone

Git commits were used throughout development to keep the implementation history visible.

---

# Phase 1 — Repository and Environment

## Repository Initialization

Created the project repository and initialized Git.

The repository was made public from the beginning so the development history remained visible.

Initial project files included:

- `.gitignore`
- `.env.example`
- `README.md`
- `BUILDLOG.md`
- `EVIDENCE.md`
- `capstone.yaml`

Initial Git checkpoint:

```text
chore: initialize capstone repository

Phase 2 — Architecture and Design

Created the system design before implementing the main application features.

The design covers:

problem definition
project goals
non-goals
technology stack
tenancy model
widget model
submission model
indexes
API contracts
embed flow
submission flow
dashboard flow

The design document is:

DESIGN.md

Git checkpoint:

docs: add system design
Phase 3 — FastAPI Foundation

Created the FastAPI application foundation.

Implemented:

FastAPI application
health endpoint
database health endpoint
environment loading
SQLAlchemy database connection
dependency-based database sessions

Health endpoints:

GET /health
GET /health/db

Git checkpoint:

feat: add FastAPI application foundation
Phase 4 — PostgreSQL and Database Schema

PostgreSQL was selected as the main persistent database.

Docker Compose was used to run PostgreSQL locally.

The initial database schema contains:

tenants
widgets
submissions

Alembic was added for database migrations.

The initial migration created:

UUID primary keys
tenant relationships
widget relationships
submission relationships
foreign keys
indexes
timestamps
JSON fields

Git checkpoint:

feat: add initial database schema
Phase 5 — Supabase Authentication

Supabase Auth was integrated for customer authentication.

The application uses the Supabase access token supplied in:

Authorization: Bearer <access-token>

The FastAPI authentication dependency validates the token through Supabase.

An authenticated Supabase user is mapped to an internal application tenant.

The application therefore separates:

Supabase identity
        ↓
Application tenant
        ↓
Tenant-owned widgets/submissions

This provides the foundation for tenant isolation.

Phase 6 — Tenant-Aware Widget CRUD

Implemented authenticated widget management.

Endpoints:

POST   /api/v1/widgets
GET    /api/v1/widgets
GET    /api/v1/widgets/{widget_id}
PATCH  /api/v1/widgets/{widget_id}
DELETE /api/v1/widgets/{widget_id}

Widget fields include:

widget type
title
description
configurable fields
button text
display options
version
timestamps

The repository layer ensures widget queries include the authenticated tenant.

Updating a widget increments its version.

Git checkpoint:

feat: add authenticated widget CRUD
Phase 7 — Public Widget Delivery

Implemented the public widget configuration endpoint:

GET /api/v1/public/widgets/{public_id}

The endpoint does not require authentication.

The response exposes only public widget configuration.

Caching was added through:

Cache-Control: public, max-age=60

The widget JavaScript bundle was added at:

/widget/v1/widget.js

The JavaScript bundle dynamically retrieves the public widget configuration and renders the widget.

Phase 8 — Embeddable Widget

Implemented a plain JavaScript embeddable widget.

Example:

<script
    src="http://127.0.0.1:8000/widget/v1/widget.js"
    data-widget="YOUR_PUBLIC_WIDGET_ID"
></script>

The widget:

identifies the configured public widget
loads its public configuration
creates the form
renders configured fields
collects visitor data
submits the data
displays success/error feedback

The widget also generates an idempotency key for each submission attempt.

Phase 9 — Cross-Origin Support

FastAPI CORS middleware was configured for the public widget flow.

Supported methods include:

GET
POST
OPTIONS

Required headers include:

Content-Type
Idempotency-Key

A separate demo page was created:

demo/index.html

The demo page runs on port 5500, while the API runs on port 8000.

This creates a genuine different-origin browser test.

The widget successfully rendered from the second origin.

Phase 10 — Submission API

Implemented the public submission endpoint:

POST /api/v1/public/widgets/{public_id}/submissions

The submission flow was structured as:

Request
  ↓
Payload parsing
  ↓
Widget lookup
  ↓
Rate limit
  ↓
Honeypot
  ↓
Field validation
  ↓
Idempotency check
  ↓
Geo enrichment
  ↓
PostgreSQL persistence
  ↓
Async side effect
  ↓
Response

Submission records store:

tenant ID
widget ID
submitted data
IP address
country
city
user agent
source origin
idempotency key
creation timestamp
Phase 11 — Submission Hardening

The public submission path was hardened against malformed and abusive requests.

Implemented:

Payload size limit

Maximum request body:

16 KB

Oversized requests return:

413 Request payload too large
Validation

Invalid payloads return controlled 4xx responses.

Validation covers:

required fields
unexpected fields
text field types
email values
Honeypot

A hidden website field is included in the widget.

Filled honeypot submissions are rejected.

Rate limiting

The local implementation uses:

5 requests / IP / 60 seconds

Requests exceeding the limit receive:

429 Too Many Requests

The current rate limiter is intentionally in-memory because this capstone is a local/single-process implementation.

Phase 12 — Idempotency

Idempotency support was added to submissions.

The API accepts:

Idempotency-Key

The key is scoped by:

tenant + widget + idempotency key

A PostgreSQL unique index prevents duplicate records for the same key.

A new Alembic migration was created:

4a1e5dbc1e1c_add_submission_idempotency_key.py

This migration was successfully applied.

Phase 13 — Geo Enrichment and Fallback

A geo service was implemented with two providers.

Provider A:

ip-api.com

Provider B:

ipapi.co

The fallback flow is:

Provider A
    ↓ failure
Provider B
    ↓ failure
Store submission without geo data

A deterministic mock mode was implemented through:

GEO_MOCK_MODE=true

Test cases:

203.0.113.10
→ Provider A succeeds

203.0.113.20
→ Provider A fails
→ Provider B succeeds

203.0.113.30
→ both providers fail
→ submission still stores

Automated tests were added for all three scenarios.

Phase 14 — Inngest Background Processing

Inngest was integrated for asynchronous side effects.

Successful submissions generate:

widget/submission.created

The background function:

process-submission-side-effects

was configured with retry handling.

The local Inngest Dev Server was used to verify the integration.

A normal test event was successfully delivered and processed.

Phase 15 — Retry and Failure Handling

A deterministic failure mode was added to the background function for testing.

The Inngest function is configured with:

retries=3

A simulated failure was triggered through a test event.

The Inngest development dashboard showed retry attempts and the simulated failure.

This provided evidence that background failures are handled separately from the primary HTTP submission flow.

Phase 16 — Dashboard APIs

Implemented authenticated dashboard endpoints:

GET /api/v1/dashboard/widgets

GET /api/v1/dashboard/widgets/{widget_id}/submissions

GET /api/v1/dashboard/widgets/{widget_id}/stats

The dashboard exposes:

tenant-owned widgets
widget submissions
total submission count
latest submission timestamp

Dashboard requests verify widget ownership before returning submissions or statistics.

Phase 17 — Automated Testing

pytest was added to the project.

A pytest.ini file was added so the project root is available on the Python path.

Automated tests cover:

valid submission data
missing required fields
unexpected fields
invalid email
invalid text values
geo Provider A success
geo Provider A → Provider B fallback
both geo providers failing
invalid IP handling
rate-limit allowance
rate-limit rejection
rate-limit reset
tenant isolation
same-tenant widget access
background side-effect enqueue failure handling

The complete test suite passed successfully:

15 passed
Phase 18 — Seed Data

A deterministic seed command was implemented:

python -m app.seed

The seed creates a demo tenant and widget if they do not already exist.

The command was executed twice.

Both executions returned the same identifiers:

Tenant ID:
6ef6191d-22d9-45f4-881a-4f733580b8a7

Widget ID:
ad9c5106-765a-4db3-8334-0fc3eb5262d0

Public ID:
33813733-0bca-4542-9c2f-0ca8ce6f49e1

This demonstrated that the seed command is idempotent.

Phase 19 — Documentation

The following documentation files were maintained:

README.md
DESIGN.md
EVIDENCE.md
BUILDLOG.md
capstone.yaml

README.md documents:

setup
architecture
API endpoints
widget embedding
testing
known limitations

DESIGN.md documents the architecture and data model.

EVIDENCE.md maps requirements to implementation and verification evidence.

BUILDLOG.md records development decisions and AI-assisted work.

AI-Assisted Development

AI tools were used during development as an implementation and reasoning assistant.

AI assistance was used for tasks including:

brainstorming architecture
reviewing API design
generating initial code structures
debugging implementation issues
reviewing errors
improving validation
generating test cases
preparing documentation
checking capstone requirement coverage

The implementation was reviewed and tested locally after AI-assisted changes.

Important development decisions were not accepted blindly. Generated code was inspected, executed, debugged, and modified as necessary.

Examples of implementation issues that were identified and corrected during development include:

Python import/test path configuration
FastAPI/Inngest integration details
controlled validation error handling
CORS configuration
database migration changes
idempotency support
Testing and Verification Philosophy

The project used both automated and manual verification.

Automated tests were used for deterministic logic such as:

validation
rate limiting
geo fallback

Manual verification was used for integration behavior such as:

authenticated API requests
PostgreSQL persistence
public widget delivery
browser CORS behavior
second-origin rendering
submission flow
Inngest event processing
Inngest retries

This combination was used because some capstone requirements depend on multiple running services and browser behavior.

Current Implementation Limitations

The project is intentionally scoped as a local-first internship capstone.

The following production-scale features are outside the current implementation:

distributed rate limiting
horizontal worker scaling
production CDN
managed production database deployment
production email delivery
production webhook delivery
advanced bot detection
production observability infrastructure

These are treated as future production concerns rather than required capstone functionality.

Final Development State

The required capstone functionality has been implemented and verified.

Current major components:

FastAPI
PostgreSQL
Alembic
Supabase Auth
Inngest
JavaScript Widget
Dashboard APIs
Geo fallback
Rate limiting
Honeypot
Idempotency
Automated tests
Second-origin demo
Seed command
Documentation

