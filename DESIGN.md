# Embeddable Widget & Lead-Capture Platform
## System Design

## 1. Problem

The platform allows customers to create embeddable widgets such as
signup forms and contact forms.

A customer receives a single JavaScript `<script>` snippet that can
be placed on another website.

Visitors interact with the widget and submit information. The backend
validates and protects the submission, enriches it with geographic
information, stores it, and exposes the submissions to the widget owner
through authenticated dashboard APIs.

The system is designed to accept requests from websites and browsers
that are outside our control.

---

## 2. Goals

The system must:

- Allow authenticated customers to create and manage widgets.
- Keep customer data isolated between tenants.
- Generate an embeddable JavaScript snippet for each widget.
- Serve widget configuration through a public endpoint.
- Serve a versioned widget JavaScript bundle.
- Accept cross-origin visitor submissions.
- Validate all public input at the API boundary.
- Protect public endpoints against abuse.
- Detect spam submissions.
- Enrich submissions using IP geolocation.
- Fall back to a second geo provider when the first fails.
- Store submissions even when geo enrichment is unavailable.
- Trigger a non-critical email/webhook side effect after storage.
- Ensure side-effect failures do not fail the submission.
- Provide authenticated dashboard APIs for submissions and analytics.

---

## 3. Non-Goals

The following are intentionally outside the scope of the core capstone:

- Building a production-grade visual form builder.
- Hosting customer websites.
- Deploying the platform to a production domain.
- Building a real CDN.
- Building a highly polished frontend dashboard.
- Supporting complex organization/team permissions.
- Implementing advanced bot protection such as CAPTCHA.

The customer website will be represented by a simple HTML page served
from a different origin during local testing.

---

## 4. Technology Stack

### Backend

- Python
- FastAPI
- Pydantic

### Authentication

- Supabase Auth
- JWT access tokens

### Database

- PostgreSQL
- Docker Compose

### Background Processing

- Inngest

### Widget

- Plain JavaScript

### Customer Test Website

- Plain HTML
- Served from a second local origin

### Geo Enrichment

Provider A:
- ip-api.com

Provider B:
- ipapi.co

### Email / Notification

- Console logging initially
- May use Mailpit for local testing

---

## 5. Tenancy Model

The core system uses a simple tenant model.

For the initial implementation:

- Each authenticated user belongs to one tenant.
- A tenant can own multiple widgets.
- A widget can have many submissions.
- Every widget and submission is associated with its tenant.

Conceptually:

    User
      |
      | 1:1
      v
    Tenant
      |
      | 1:N
      v
    Widget
      |
      | 1:N
      v
    Submission

Tenant isolation is enforced by backend queries.

The application must never rely on the frontend to enforce tenant
boundaries.

An authenticated user can only read, update, or delete widgets belonging
to their tenant.

Dashboard submission queries must also be restricted to the authenticated
user's tenant.

---

## 6. Data Model

### Tenant

Fields:

- id
- name
- created_at

### Widget

Fields:

- id
- tenant_id
- public_id
- type
- title
- description
- fields
- button_text
- display_options
- version
- created_at
- updated_at

### Submission

Fields:

- id
- tenant_id
- widget_id
- data
- ip_address
- country
- city
- user_agent
- source_origin
- created_at

---

## 7. Important Database Indexes

The database will include indexes for common access patterns.

Planned indexes:

- `widgets.tenant_id`
- `widgets.public_id`
- `submissions.tenant_id`
- `submissions.widget_id`
- `submissions.created_at`

`widgets.public_id` will be unique because it is used by the public
embed URL.

---

## 8. Widget Types

The initial implementation will support:

- signup
- contact

The data model will allow additional widget types later.

---

## 9. Embed Flow

The customer creates a widget through the authenticated API.

The API returns an embed snippet similar to:

    <script
      src="http://localhost:8000/widget.js?id=abc123">
    </script>

The customer places this script on their website.

The widget script:

1. Reads the widget public ID.
2. Requests the widget configuration.
3. Receives the public configuration.
4. Renders the widget.
5. Collects visitor input.
6. Sends the submission to the public submission endpoint.

The customer test website will run on a different origin from the API.

Example:

    API:
    http://localhost:8000

    Customer website:
    http://localhost:5500

---

## 10. Public Widget Configuration

Endpoint:

    GET /api/v1/widgets/{public_id}/config

This endpoint is public.

It must:

- Return only information required by the widget.
- Never expose tenant-private information.
- Support CORS.
- Return appropriate `Cache-Control` headers.
- Return a small response payload.

---

## 11. Versioned Widget Bundle

The widget JavaScript will be served as a versioned asset.

Example:

    /widget.v1.js

When the widget bundle changes, the version can change.

The bundle can therefore use long-lived caching without forcing clients
to receive stale code.

---

## 12. Widget Management API

Authenticated endpoints will provide CRUD operations.

Planned endpoints:

    POST   /api/v1/widgets
    GET    /api/v1/widgets
    GET    /api/v1/widgets/{id}
    PATCH  /api/v1/widgets/{id}
    DELETE /api/v1/widgets/{id}

All management endpoints require valid authentication.

All queries must enforce tenant isolation.

---

## 13. Submission API

Public endpoint:

    POST /api/v1/submissions

The endpoint must:

1. Accept cross-origin requests.
2. Handle CORS preflight requests.
3. Validate the request payload.
4. Reject malformed input with a 4xx response.
5. Reject oversized input.
6. Apply rate limiting.
7. Check the spam-control mechanism.
8. Extract the visitor IP.
9. Attempt geo enrichment.
10. Fall back to the second provider if necessary.
11. Store the submission.
12. Trigger the non-critical side effect.

The main submission must succeed even when geo enrichment or the
side effect fails.

---

## 14. Abuse Protection

The public submission endpoint will use:

### Rate limiting

Requests will be limited based on:

- IP address
- Widget

Excessive requests will receive:

    429 Too Many Requests

### Spam protection

The widget will contain a honeypot field.

Normal users should leave the field empty.

A submission containing a value in the honeypot field will be treated
as spam and rejected or silently dropped.

---

## 15. Geo Enrichment

The enrichment flow is:

    Visitor IP
        |
        v
    Provider A
        |
        | failure
        v
    Provider B
        |
        | failure
        v
    No geo data

Provider A:

    ip-api.com

Provider B:

    ipapi.co

If both providers fail, the submission is still stored.

The fallback behavior will be tested deterministically using mock
providers so that failure scenarios can be reproduced reliably.

---

## 16. Safe Side Effects

After the submission has been stored, the system will trigger a
background operation for a confirmation email, webhook, or notification.

The side effect is non-critical.

Therefore:

    Store submission
          |
          +----> background side effect
                     |
                     +---- success
                     |
                     +---- failure

A side-effect failure must never cause the original submission request
to fail.

---

## 17. Dashboard API

Authenticated dashboard endpoints will provide:

- Submission list
- Submission counts
- Per-widget statistics
- Counts over time
- Geographic breakdown

The dashboard itself will remain intentionally simple because the
capstone is focused primarily on backend behavior.

---

## 18. Layered Architecture

The backend will separate:

    HTTP / API Layer
          |
          v
    Business / Service Layer
          |
          v
    Repository / Data Layer
          |
          v
    PostgreSQL

External services such as geo providers and notification systems will
be isolated behind service interfaces so they can be mocked during
testing.

---

## 19. Security Principles

The backend will follow these principles:

- Never trust client input.
- Validate input at the API boundary.
- Never expose tenant-private data through public endpoints.
- Authenticate owner/admin endpoints.
- Enforce tenant isolation in database queries.
- Never commit secrets.
- Keep credentials in environment variables.
- Avoid logging sensitive credentials.
- Apply rate limits to public endpoints.

---

## 20. Testing Strategy

The implementation will include tests for:

- Authentication
- Tenant isolation
- Widget CRUD
- Invalid payloads
- Oversized payloads
- CORS preflight
- Rate limiting
- Honeypot spam detection
- Geo provider A fallback
- Both geo providers failing
- Side-effect failure
- Successful cross-origin submission

The final implementation will also be manually tested from the
second-origin customer HTML page.

---

## 21. Success Criteria

The system is complete when:

1. An authenticated owner can create and manage widgets.
2. Tenant isolation is demonstrably enforced.
3. A widget generates an embed snippet.
4. The widget loads from a different origin.
5. The public config endpoint is cached.
6. Cross-origin submissions work.
7. Invalid input produces clean 4xx responses.
8. Rate limiting produces 429 responses.
9. Spam submissions are blocked.
10. Geo enrichment uses the fallback chain.
11. Submissions succeed even when geo providers are unavailable.
12. Side-effect failures do not prevent storage.
13. Dashboard APIs expose submissions and basic analytics.
# Embeddable Widget & Lead-Capture Platform
## System Design

## 1. Problem

The platform allows customers to create embeddable widgets such as
signup forms and contact forms.

A customer receives a single JavaScript `<script>` snippet that can
be placed on another website.

Visitors interact with the widget and submit information. The backend
validates and protects the submission, enriches it with geographic
information, stores it, and exposes the submissions to the widget owner
through authenticated dashboard APIs.

The system is designed to accept requests from websites and browsers
that are outside our control.

---

## 2. Goals

The system must:

- Allow authenticated customers to create and manage widgets.
- Keep customer data isolated between tenants.
- Generate an embeddable JavaScript snippet for each widget.
- Serve widget configuration through a public endpoint.
- Serve a versioned widget JavaScript bundle.
- Accept cross-origin visitor submissions.
- Validate all public input at the API boundary.
- Protect public endpoints against abuse.
- Detect spam submissions.
- Enrich submissions using IP geolocation.
- Fall back to a second geo provider when the first fails.
- Store submissions even when geo enrichment is unavailable.
- Trigger a non-critical email/webhook side effect after storage.
- Ensure side-effect failures do not fail the submission.
- Provide authenticated dashboard APIs for submissions and analytics.
- Support idempotent submission attempts.

---

## 3. Non-Goals

The following are intentionally outside the scope of the core capstone:

- Building a production-grade visual form builder.
- Hosting customer websites.
- Deploying the platform to a production domain.
- Building a real CDN.
- Building a highly polished frontend dashboard.
- Supporting complex organization/team permissions.
- Implementing advanced bot protection such as CAPTCHA.
- Building distributed rate limiting.
- Building production-grade email delivery.

The customer website will be represented by a simple HTML page served
from a different origin during local testing.

---

## 4. Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- psycopg2-binary

### Authentication

- Supabase Auth
- JWT access tokens

### Database

- PostgreSQL
- Docker Compose
- Alembic migrations

### Background Processing

- Inngest

### Widget

- Plain JavaScript

### Customer Test Website

- Plain HTML
- Served from a second local origin

### Geo Enrichment

Provider A:

- ip-api.com

Provider B:

- ipapi.co

### Email / Notification

- Console logging initially
- Inngest background processing

---

## 5. Tenancy Model

The core system uses a simple tenant model.

For the implementation:

- Each authenticated Supabase user belongs to one application tenant.
- A tenant can own multiple widgets.
- A widget can have many submissions.
- Every widget and submission is associated with its tenant.
- The Supabase user ID is stored on the tenant as the external identity reference.

Conceptually:

    Supabase User
          |
          | 1:1
          v
       Tenant
          |
          | 1:N
          v
       Widget
          |
          | 1:N
          v
     Submission

Tenant isolation is enforced by backend queries.

The application must never rely on the frontend to enforce tenant
boundaries.

An authenticated user can only read, update, or delete widgets belonging
to their tenant.

Dashboard submission queries must also be restricted to the authenticated
user's tenant.

Public widget access uses a non-secret `public_id` and exposes only the
configuration required for rendering.

---

## 6. Data Model

### Tenant

Fields:

- id
- supabase_user_id
- name
- created_at

`supabase_user_id` uniquely maps the application tenant to the
authenticated Supabase user.

### Widget

Fields:

- id
- tenant_id
- public_id
- type
- title
- description
- fields
- button_text
- display_options
- version
- created_at
- updated_at

`public_id` is exposed to customer websites and is separate from the
internal widget ID.

### Submission

Fields:

- id
- tenant_id
- widget_id
- idempotency_key
- data
- ip_address
- country
- city
- user_agent
- source_origin
- created_at

The `idempotency_key` allows clients to safely retry an important
submission without intentionally creating duplicate records.

---

## 7. Important Database Indexes

The database includes indexes for common access patterns.

Indexes include:

- `widgets.tenant_id`
- `widgets.public_id`
- `submissions.tenant_id`
- `submissions.widget_id`
- `submissions.created_at`

`widgets.public_id` is unique because it is used by the public embed flow.

The submission table also has a unique constraint covering:

- tenant
- widget
- idempotency key

This prevents duplicate records when the same idempotency key is reused
for the same widget.

---

## 8. Widget Types

The initial implementation supports:

- signup
- contact

The data model allows additional widget types later.

---

## 9. Embed Flow

The customer creates a widget through the authenticated API.

The application provides a public widget ID that can be placed in an
embed snippet similar to:

    <script
      src="http://127.0.0.1:8000/widget/v1/widget.js"
      data-widget="YOUR_PUBLIC_WIDGET_ID"
    ></script>

The widget script:

1. Reads the widget public ID.
2. Determines the API origin from the script URL unless explicitly
   configured.
3. Requests the public widget configuration.
4. Receives the public configuration.
5. Renders the widget.
6. Collects visitor input.
7. Generates an idempotency key.
8. Sends the submission to the public submission endpoint.
9. Displays success or error feedback.

The customer test website runs on a different origin from the API.

Example:

    API:
        http://127.0.0.1:8000

    Customer website:
        http://127.0.0.1:5500

---

## 10. Public Widget Configuration

Endpoint:

    GET /api/v1/public/widgets/{public_id}

This endpoint is public.

It:

- Returns only information required by the widget.
- Does not expose tenant-private information.
- Supports cross-origin access.
- Returns `Cache-Control: public, max-age=60`.
- Returns a small JSON configuration payload.

The public response includes the widget's current version.

---

## 11. Versioned Widget Bundle

The widget JavaScript is served as:

    /widget/v1/widget.js

The `/v1/` path provides an explicit bundle version namespace.

When a future breaking widget implementation is introduced, a new
versioned bundle path can be introduced without silently replacing the
existing version.

---

## 12. Widget Management API

Authenticated endpoints provide CRUD operations.

Implemented endpoints:

    POST   /api/v1/widgets
    GET    /api/v1/widgets
    GET    /api/v1/widgets/{id}
    PATCH  /api/v1/widgets/{id}
    DELETE /api/v1/widgets/{id}

All management endpoints require valid authentication.

All queries enforce tenant isolation.

Updating a widget increments its version.

---

## 13. Submission API

Public endpoint:

    POST /api/v1/public/widgets/{public_id}/submissions

The endpoint:

1. Accepts cross-origin requests.
2. Handles CORS preflight requests.
3. Enforces a maximum request body size.
4. Validates the request payload.
5. Rejects malformed input with a 4xx response.
6. Applies rate limiting.
7. Checks the honeypot spam-control mechanism.
8. Validates submitted fields against the widget configuration.
9. Checks the idempotency key.
10. Extracts the visitor IP.
11. Attempts geo enrichment.
12. Falls back to the second provider if necessary.
13. Stores the submission.
14. Attempts to enqueue the non-critical background side effect.
15. Returns the stored submission result.

The main submission must succeed even when geo enrichment or the
background side effect fails.

---

## 14. Abuse Protection

The public submission endpoint uses multiple layers of protection.

### Rate limiting

The current local implementation limits requests by client IP.

The configured limit is:

- 5 requests
- per IP
- per 60 seconds

Excessive requests receive:

    429 Too Many Requests

The limiter is intentionally in-memory because this capstone is a
local/single-process implementation.

A production deployment would use a distributed rate limiter.

### Payload size protection

Public submission request bodies are limited to:

    16 KB

Oversized requests receive:

    413 Request payload too large

### Spam protection

The widget contains a hidden honeypot field.

Normal users should leave the field empty.

A submission containing a value in the honeypot field is rejected with a
controlled 4xx response.

---

## 15. Geo Enrichment

The enrichment flow is:

    Visitor IP
        |
        v
    Provider A
        |
        | failure
        v
    Provider B
        |
        | failure
        v
    No geo data
        |
        v
    Store submission

Provider A:

    ip-api.com

Provider B:

    ipapi.co

If both providers fail, the submission is still stored with:

    country = null
    city = null

The implementation supports deterministic mock mode through:

    GEO_MOCK_MODE=true

This allows Provider A success, Provider A → Provider B fallback, and
both-provider failure to be reproduced without depending on external
provider availability.

---

## 16. Safe Side Effects

After the submission has been stored, the system attempts to trigger an
asynchronous operation for a confirmation email, webhook, or notification.

The side effect is non-critical.

The primary flow is:

    Store submission
          |
          +----> enqueue background event
                       |
                       +---- success
                       |
                       +---- failure -> log alert

The Inngest background function is separately responsible for processing
the side effect.

The background function is configured with retries.

A side-effect failure must never cause the original submission request to
fail.

---

## 17. Idempotency

The public submission API accepts:

    Idempotency-Key

The key is scoped by:

    tenant + widget + idempotency key

The database enforces uniqueness for this combination.

When a client retries a submission using the same key for the same widget,
the existing submission is returned instead of intentionally creating
another record.

The widget automatically generates a unique idempotency key for each
normal submission attempt.

---

## 18. Dashboard API

Authenticated dashboard endpoints provide:

    GET /api/v1/dashboard/widgets

    GET /api/v1/dashboard/widgets/{widget_id}/submissions

    GET /api/v1/dashboard/widgets/{widget_id}/stats

The dashboard exposes:

- Tenant-owned widgets.
- Widget submissions.
- Total submission count.
- Latest submission timestamp.
- Submission geographic fields when available.

Dashboard access requires authentication.

Dashboard widget queries verify that the requested widget belongs to the
authenticated tenant before returning submissions or statistics.

The dashboard UI itself remains intentionally outside the main scope of
this backend-focused capstone.

---

## 19. Layered Architecture

The backend separates:

    HTTP / API Layer
          |
          v
    Business / Service Layer
          |
          v
    Repository / Data Layer
          |
          v
    PostgreSQL

The project structure follows this separation:

    app/api/
    app/services/
    app/repositories/
    app/models/
    app/schemas/

External services such as geo providers and notification systems are
isolated behind service-level interfaces so deterministic behavior can be
tested.

---

## 20. Security Principles

The backend follows these principles:

- Never trust client input.
- Validate input at the API boundary.
- Never expose tenant-private data through public endpoints.
- Authenticate owner/admin endpoints.
- Enforce tenant isolation in backend queries.
- Never commit secrets.
- Keep credentials in environment variables.
- Avoid logging authentication credentials.
- Apply rate limits to public submission endpoints.
- Limit public request payload size.
- Use idempotency controls for retryable submissions.

---

## 21. Testing Strategy

The implementation includes automated tests for deterministic behavior
and manual tests for multi-service/browser behavior.

Automated tests cover:

- Valid submission data.
- Missing required fields.
- Unexpected fields.
- Invalid email.
- Invalid text values.
- Geo Provider A success.
- Geo Provider A → Provider B fallback.
- Both geo providers failing.
- Invalid IP handling.
- Rate-limit allowance.
- Rate-limit rejection.
- Rate-limit window reset.
- Tenant isolation.
- Same-tenant widget access.
- Background side-effect enqueue failure handling.

Manual verification covers:

- Authentication.
- PostgreSQL persistence.
- Widget CRUD.
- Public widget configuration.
- Cache-Control headers.
- CORS preflight.
- Cross-origin widget rendering.
- Cross-origin submission.
- Payload-size rejection.
- Honeypot rejection.
- Idempotent submission behavior.
- Inngest event processing.
- Inngest retry behavior.
- Dashboard APIs.
- Deterministic seed behavior.

The final implementation is also manually tested from the second-origin
customer HTML page.

---

## 22. Success Criteria

The system is complete when:

1. An authenticated owner can create and manage widgets.
2. Tenant isolation is demonstrably enforced.
3. A widget provides an embeddable script snippet.
4. The widget loads from a different origin.
5. The public config endpoint is cached.
6. Cross-origin submissions work.
7. Invalid input produces clean 4xx responses.
8. Oversized input produces a controlled 413 response.
9. Rate limiting produces 429 responses.
10. Spam submissions are blocked.
11. Geo enrichment uses the fallback chain.
12. Submissions succeed even when geo providers are unavailable.
13. Idempotent retries do not intentionally create duplicates.
14. Side-effect failures do not prevent submission storage.
15. Dashboard APIs expose submissions and basic analytics.
16. A background job exists with retry handling.
17. A deterministic seed command is available.
18. Automated tests pass.
19. A second-origin browser demo works.
20. All requirements have evidence in `EVIDENCE.md`.