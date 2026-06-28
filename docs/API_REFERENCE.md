# API Reference — AI Sales Copilot

> Complete endpoint reference for the AI Sales Copilot REST API.
> Base URL: `http://localhost:8000/api/v1`

---

## Authentication

All endpoints (except register/login) require a Bearer token in the `Authorization` header.

```
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@company.com",
  "password": "secureP@ssw0rd",
  "full_name": "John Doe",
  "role": "sales_rep"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@company.com",
  "full_name": "John Doe",
  "role": "sales_rep"
}
```

### POST `/auth/login`
Authenticate and receive JWT tokens.

**Request Body:** `application/x-www-form-urlencoded`
- `username`: User email
- `password`: User password

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer"
}
```

### POST `/auth/mfa/setup`
Generate TOTP secret for Google Authenticator enrollment.

**Response:** `200 OK`
```json
{
  "mfa_enabled": true,
  "otp_secret": "OSCA5JHYMJI6PAFC75HF3QTKSZ35TULB",
  "qr_code_url": "otpauth://totp/SalesCopilot:user@company.com?secret=...",
  "backup_codes": ["REC-1234-ABCD", "REC-5678-EFGH"]
}
```

### POST `/auth/mfa/verify`
Validate a 6-digit TOTP code from Google Authenticator.

**Request Body:**
```json
{
  "code": "123456",
  "otp_secret": "OSCA5JHYMJI6PAFC75HF3QTKSZ35TULB"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "access_token": "mfa_verified_token..."
}
```

---

## Security & Compliance Endpoints

### GET `/security/audit`
Retrieve the audit trail. Supports ABAC region filtering via `X-User-Region` header.

**Headers:**
- `X-User-Region`: `us-east` (required for access; other regions blocked by ABAC policy)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "action": "recommendation.approved",
    "entity": "Recommendation",
    "entity_id": 42,
    "timestamp": "2026-06-27T10:00:00"
  }
]
```

### GET `/security/export-pdf`
Download a styled executive PDF report.

**Response:** `200 OK` (`application/pdf`)

### GET `/security/events`
Get recent security event alerts (failed logins, guardrail triggers).

### GET `/security/sessions`
List all active user sessions with device and IP information.

### POST `/security/logout-all`
Revoke and terminate all active user sessions.

---

## Real-Time Streaming

### GET `/stream/planner`
Server-Sent Events (SSE) stream publishing real-time agent execution updates.

**Response:** `text/event-stream`
```
event: update
data: {"node": "planner", "message": "Planner compiled agent itinerary", "status": "start", "time": "0.1s"}

event: update
data: {"node": "crm", "message": "CRM profile fields mapped", "status": "agent", "time": "0.4s"}

event: update
data: {"node": "recommendation", "message": "AI NBA generation complete", "status": "complete", "time": "2.1s"}
```

---

## Customer Endpoints

### GET `/customers`
List all customers with pagination and filtering.

**Query Parameters:**
- `skip` (int): Offset (default: 0)
- `limit` (int): Page size (default: 100)
- `industry` (string): Filter by industry
- `stage` (string): Filter by CRM stage

### POST `/customers`
Create a new customer.

### GET `/customers/{id}`
Get customer by ID.

### PUT `/customers/{id}`
Update customer.

### DELETE `/customers/{id}`
Delete customer.

---

## Recommendation Endpoints

### GET `/recommendations`
List recommendations with status filtering.

**Query Parameters:**
- `status` (string): `pending_review`, `approved`, `rejected`, `escalated`
- `customer_id` (int): Filter by customer

### POST `/recommendations`
Create a recommendation (typically by AI agent).

### PUT `/recommendations/{id}`
Update recommendation status or content.

---

## Human-in-the-Loop Review

### POST `/review/approve/{id}`
Approve a recommendation for execution.

### POST `/review/reject/{id}`
Reject a recommendation with feedback.

### POST `/review/escalate/{id}`
Escalate a recommendation to a senior reviewer.

---

## AI Agent Endpoints

### POST `/agent/execute`
Trigger a full LangGraph multi-agent workflow execution for a customer.

**Request Body:**
```json
{
  "customer_id": 1,
  "query": "Generate next best actions for Acme Corporation"
}
```

---

## Analytics Endpoints

### GET `/analytics/summary`
Get BI dashboard summary metrics.

### GET `/analytics/funnel`
Get sales deal stage funnel breakdown.

### GET `/analytics/forecast`
Get revenue time-series forecast data.

---

## Knowledge Base Endpoints

### GET `/knowledge`
List indexed knowledge documents.

### POST `/knowledge`
Upload and index a new document (PDF, DOCX, TXT, CSV).

**Request:** `multipart/form-data`
- `file`: Document file (max 10MB)
- `title`: Document title

---

## Search Endpoints

### GET `/search/global`
Cross-entity semantic search across customers, meetings, emails, knowledge, and recommendations.

**Query Parameters:**
- `q` (string): Search query
- `entities` (string): Comma-separated entity types to search

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error description",
  "status_code": 400
}
```

| Status Code | Meaning |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized (invalid/expired token) |
| 403 | Forbidden (insufficient permissions / ABAC violation) |
| 404 | Resource Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |
