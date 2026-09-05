# FlyRank Capstone — Evidence

This document maps the capstone requirements to implementation and verification evidence.

---

## 1. Authenticated Widget Management

### Requirement

Authenticated customers must be able to create, read, update, and delete widgets.

### Implementation

Widget management is implemented through:

```text
POST   /api/v1/widgets
GET    /api/v1/widgets
GET    /api/v1/widgets/{widget_id}
PATCH  /api/v1/widgets/{widget_id}
DELETE /api/v1/widgets/{widget_id}

Authentication is handled through Supabase Auth access tokens.

The application resolves the authenticated Supabase user to an internal tenant.

Evidence

Manual API testing verified:

authenticated widget creation
widget listing
widget retrieval
widget update
widget deletion
unauthenticated access rejection

The widget update operation increments the widget version.

2. Tenant Isolation
Requirement

Tenant A must not be able to access Tenant B's widgets or submissions.

Implementation

Every authenticated request resolves the current tenant.

Widget repository queries use the tenant ID:

Widget.id == requested_widget_id
AND
Widget.tenant_id == current_tenant_id

Dashboard submission queries similarly require the authenticated tenant ID.

Evidence

Tenant ownership checks are implemented in:

app/api/tenant.py
app/repositories/widget.py
app/repositories/dashboard.py
app/api/dashboard.py

A widget belonging to another tenant is returned as:

404 Widget not found

rather than being exposed.

3. Database Persistence
Requirement

The platform must use real persistence with an appropriate schema and indexes.

Implementation

PostgreSQL is used as the persistent database.

The main tables are:

tenants
widgets
submissions

Alembic manages schema migrations.

The schema includes:

UUID primary keys
foreign keys
tenant ownership
widget public IDs
submission timestamps
submission metadata
idempotency keys
indexes for common queries
Evidence

Database migrations successfully applied with:

alembic upgrade head

PostgreSQL health was verified with:

docker compose exec db pg_isready -U postgres -d widget_platform

The API database health endpoint also returns a successful database check.

4. Public Widget Configuration
Requirement

The public widget configuration must be accessible without authentication.

Implementation
GET /api/v1/public/widgets/{public_id}

The endpoint returns:

public widget ID
widget type
title
description
fields
button text
display options
version
Evidence

The endpoint was manually tested without an Authorization header and returned:

200 OK

The response also includes:

Cache-Control: public, max-age=60
5. Embeddable JavaScript
Requirement

Customers must receive a simple script that can be embedded on an external website.

Implementation

The versioned JavaScript bundle is served at:

/widget/v1/widget.js

Example:

<script
    src="http://127.0.0.1:8000/widget/v1/widget.js"
    data-widget="YOUR_PUBLIC_WIDGET_ID"
></script>

The script:

identifies the widget
retrieves its public configuration
creates the widget UI
collects visitor data
submits the data to the API
displays success/error status
Evidence

The widget successfully rendered in the separate-origin demo page.

6. Cross-Origin Rendering
Requirement

The widget must work when embedded on another origin.

Implementation

The demo page is served separately from the API:

Demo:
http://127.0.0.1:5500

API:
http://127.0.0.1:8000

These are different origins.

FastAPI CORS middleware permits the required public widget methods and headers.

Evidence

The widget successfully loaded and rendered on:

http://127.0.0.1:5500

while retrieving configuration from:

http://127.0.0.1:8000
7. CORS Preflight
Requirement

Cross-origin submission must correctly handle browser OPTIONS requests.

Evidence

A preflight request was tested with:

Origin: http://127.0.0.1:5500
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type,idempotency-key

Result:

200

Returned headers included:

Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers:
Accept, Accept-Language, Content-Language,
Content-Type, Idempotency-Key
8. Submission Validation
Requirement

Malformed or invalid submissions must return clean 4xx JSON responses rather than 500 errors.

Implementation

The submission API validates:

JSON structure
maximum payload size
required widget fields
allowed field names
text field types
email field format
Evidence

Automated tests verify:

missing required field → 422
unexpected field → 422
invalid email → 422
invalid text field → 422

Malformed request bodies are converted into controlled 422 responses.

9. Payload Size Protection
Requirement

Oversized payloads must be rejected safely.

Implementation

The submission API limits request bodies to:

16 KB

Both declared Content-Length and actual request body size are checked.

Evidence

Oversized requests are handled with:

413 Request payload too large

instead of causing a server error.

10. Rate Limiting
Requirement

Submission bursts must be limited and return HTTP 429 when the limit is exceeded.

Implementation

The current local implementation allows:

5 requests / IP / 60 seconds

The sixth request within the window is rejected.

Evidence

Automated tests verify:

first five requests are accepted
sixth request is rejected
the limit resets after the time window

Expected rejection:

429 Too Many Requests
11. Honeypot Spam Protection
Requirement

The submission flow must contain a basic spam-control mechanism.

Implementation

The widget includes a hidden:

website

honeypot field.

If a submission fills the honeypot, the API rejects it.

Evidence

The honeypot is generated by:

app/static/widget.js

and checked by:

app/api/public_submissions.py

The API returns:

400 Invalid submission

when the honeypot is populated.

12. Geo Enrichment
Requirement

The platform must enrich submissions with geographic information.

Implementation

The service uses two providers:

Provider A: ip-api.com

Provider B: ipapi.co

The fallback sequence is:

Provider A
    ↓ failure
Provider B
    ↓ failure
Store without geo data
Deterministic Test Mode

The environment variable:

GEO_MOCK_MODE=true

provides deterministic testing.

Test cases:

203.0.113.10
→ Provider A succeeds

203.0.113.20
→ Provider A fails
→ Provider B succeeds

203.0.113.30
→ Provider A fails
→ Provider B fails
→ submission still stores
Evidence

Automated tests verify all three scenarios.

13. Persistence When Geo Providers Fail
Requirement

A geo provider outage must not prevent a valid submission from being stored.

Implementation

Geo lookup failures return an empty geo result:

country = null
city = null

The submission is then persisted normally.

Evidence

The deterministic both-provider-failure case returns:

{"country": null, "city": null}

without raising an exception.

14. Idempotency
Requirement

Important submission operations should avoid accidental duplicate records.

Implementation

The public submission API accepts:

Idempotency-Key

The key is scoped to:

tenant + widget + idempotency key

A unique database index enforces this constraint.

Evidence

The database migration:

4a1e5dbc1e1c_add_submission_idempotency_key.py

creates the idempotency field and unique index.

The widget automatically generates an idempotency key for each submission attempt.

15. Background Job
Requirement

At least one background job must exist.

Implementation

Successful submissions generate the Inngest event:

widget/submission.created

The event is processed by:

process-submission-side-effects

implemented in:

app/jobs/submission.py
Evidence

The local Inngest Dev Server successfully synchronized the FastAPI application and registered the function.

A test event was sent successfully.

16. Background Job Retries
Requirement

Background processing must include retries.

Implementation

The Inngest function is configured with:

retries=3
Evidence

A deterministic failure was triggered using the Inngest test event.

The Inngest development dashboard showed retry attempts and the simulated failure.

This demonstrates that side-effect failures are handled asynchronously with retry behavior.

17. Side-Effect Failure Must Not Block Submission
Requirement

A failing email/webhook or other non-critical side effect must not cause the primary submission to fail.

Implementation

The HTTP submission is persisted before asynchronous side-effect processing.

The API attempts to enqueue the Inngest event.

If event delivery itself fails, the exception is caught and logged as a side-effect alert rather than being returned as a submission failure.

The actual background job also has retry behavior.

Evidence

The architecture separates:

submission persistence

from:

background side effects

so the primary submission path does not depend on successful completion of the side effect.

18. Dashboard APIs
Requirement

Customers must be able to inspect their widgets and submissions.

Implementation

Dashboard endpoints:

GET /api/v1/dashboard/widgets

GET /api/v1/dashboard/widgets/{widget_id}/submissions

GET /api/v1/dashboard/widgets/{widget_id}/stats

Statistics include:

total submissions
latest submission timestamp
Evidence

Dashboard API implementation is contained in:

app/api/dashboard.py
app/services/dashboard.py
app/repositories/dashboard.py
app/schemas/dashboard.py

Dashboard access requires authentication and tenant ownership.

19. Seed Command
Requirement

A stranger should be able to create deterministic demo data using a seed step.

Implementation
python -m app.seed
Evidence

The command was executed twice.

First execution:

Tenant ID: 6ef6191d-22d9-45f4-881a-4f733580b8a7
Widget ID: ad9c5106-765a-4db3-8334-0fc3eb5262d0
Public ID: 33813733-0bca-4542-9c2f-0ca8ce6f49e1

Second execution returned the same IDs.

Therefore the seed command is idempotent and does not create duplicate demo records.

20. Automated Test Suite
Evidence

The project uses pytest.

Run:

pytest -v

The test suite currently covers:

submission validation
required fields
unexpected fields
email validation
text validation
geo provider A success
geo provider A → provider B fallback
both geo providers failing
invalid IP handling
rate limiting
rate-limit window reset

The suite has passed successfully with:

15 passed
21. Secrets and Environment Configuration
Requirement

Secrets must not be committed.

Implementation

Sensitive local configuration is stored in:

.env

The .env file is excluded through .gitignore.

The repository contains:

.env.example

with placeholder configuration.

Evidence

The repository does not require real Supabase credentials to be committed.

22. Layered Architecture
Requirement

Data access, business logic, and HTTP handling should be separated.

Implementation

The project separates:

app/api/
app/services/
app/repositories/
app/models/
app/schemas/

Examples:

HTTP
→ app/api/public_submissions.py

Business logic
→ app/services/submission.py

Persistence
→ app/repositories/submission.py

Database model
→ app/models/submission.py

This separation keeps HTTP concerns independent from persistence logic.

23. Design Documentation
Evidence

The system design is documented in:

DESIGN.md

It covers:

goals
non-goals
architecture
tenancy
data model
indexes
API contracts
embed flow
submission flow
dashboard APIs
24. Second-Origin Browser Proof
Requirement

The widget must render on an external customer page.

Evidence

The customer demo page is:

demo/index.html

It is served from:

http://127.0.0.1:5500

The widget API runs on:

http://127.0.0.1:8000

The widget successfully rendered on the separate-origin page and successfully submitted data to the API.

Final Requirement Summary
Requirement	Status
Authenticated widget CRUD	Complete
Tenant isolation	Complete
PostgreSQL persistence	Complete
Database migrations	Complete
Public widget config	Complete
Cache-Control	Complete
Versioned widget JS	Complete
Cross-origin rendering	Complete
CORS OPTIONS	Complete
Submission validation	Complete
Payload size protection	Complete
Rate limiting	Complete
Honeypot spam protection	Complete
Geo Provider A	Complete
Geo Provider B fallback	Complete
Store when geo unavailable	Complete
Idempotency	Complete
Background job	Complete
Retry handling	Complete
Side-effect isolation	Complete
Dashboard APIs	Complete
Seed command	Complete
Automated tests	Complete
Second-origin demo	Complete
Secrets excluded from Git	Complete
Layered architecture	Complete
Design documentation	Complete
