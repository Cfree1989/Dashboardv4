# Authentication Architecture

This document details the authentication and attribution system used in the 3D Print System.

## Authentication Philosophy

The 3D Print System uses a hybrid authentication model designed for a high-turnover, shared-terminal environment. This approach prioritizes operational simplicity while maintaining strict per-action accountability.

Key principles:
- **Workstation-level authentication** instead of individual user logins
- **Mandatory per-action staff attribution** for accountability
- **Clear separation** between workstation identity and staff member attribution
- **Resilience** against staff turnover and session management challenges

## 1. Workstation & Attribution Model

### 1.1 Workstation Login

- Each physical computer terminal is treated as a "Workstation" with its own shared password
- No individual user accounts or passwords are required for staff
- Workstation login initiates a long-lived session (e.g., 12 hours) for that specific computer
- Session is managed via JWT stored securely in the browser

### 1.2 Per-Action Attribution

- Every state-changing operation (approve, reject, update status, etc.) **requires** attribution
- Staff must select their name from a dropdown list of active staff members
- API endpoints for these actions require a `staff_name` field in the request body
- The backend validates that the selected name is on the official staff list

### 1.3 Authentication Flow

1. Staff member opens the dashboard in browser
2. System checks for valid JWT
3. If no valid JWT exists, redirects to workstation login page
4. Staff enters workstation ID and shared password
5. System validates credentials and issues a JWT containing:
   - `workstation_id` (e.g., "Front-Desk-Computer")
   - `exp` (expiration timestamp, typically 12 hours)
6. JWT is stored securely in the browser
7. All subsequent API requests include `Authorization: Bearer <token>` header
8. Protected API endpoints validate the JWT and extract workstation context

### 1.4 Attribution UI

- Every state-changing modal (approve, reject, etc.) includes a **mandatory** dropdown
- Dropdown is labeled "Performing Action As:" and lists all active staff members
- Selection cannot be skipped; it's a required field before form submission
- The UI prominently displays the logged-in workstation name at all times

## 2. Staff Turnover Management

### 2.1 Staff Onboarding

1. Administrator adds new staff member through the dashboard's staff management interface
2. System stores the new name in the `Staff` table with `is_active = true`
3. Name immediately appears in attribution dropdowns on all workstations
4. New staff names are visually highlighted in dropdowns for a configurable period

### 2.2 Staff Offboarding

1. Administrator marks departing staff as inactive through the dashboard
2. System updates the staff record with `is_active = false` and sets `deactivated_at` timestamp
3. Name no longer appears in attribution dropdowns for new actions
4. Historical attributions remain unchanged, preserving the audit trail
5. Inactive staff are visually distinguished in historical event logs

## 3. Student Authentication: Email Confirmation Model

Students do not have accounts or passwords. Their identity and approval for print jobs are handled via secure, one-time-use email links.

### 3.1 Confirmation Flow

1. When staff approves a job, the system generates a unique token using a library like `itsdangerous`
2. This token is embedded into a URL pointing to the confirmation page (`/confirm/<token>`)
3. The URL is included in an email sent to the student's email address
4. When the student clicks the link, the system validates the token
5. If valid, the job is confirmed and moved to the next status
6. This process is entirely stateless, requiring no persistent session or cookie

### 3.2 Token Security

- Tokens are cryptographically signed to prevent tampering
- Each token is specific to a single job and can only be used once
- Tokens expire after a configured period (typically 72 hours)
- If a token expires, the system provides a way to request a new one (rate-limited)

## 4. API Authentication

### 4.1 JWT Implementation

- Tokens are generated using a secure library with industry-standard algorithms
- Payload includes minimal information: `workstation_id` and expiration
- Authentication middleware validates tokens on all protected endpoints
- Invalid or expired tokens result in 401 Unauthorized responses

### 4.2 Protected Endpoints

- All staff-facing endpoints require valid JWT in the Authorization header
- Public endpoints (student submission, confirmation) do not require authentication
- Rate limiting is applied to protect public endpoints from abuse

### 4.3 Example Authentication Request/Response

**Login Request:**
```
POST /api/auth/login
Content-Type: application/json

{
  "workstation_id": "front-desk",
  "password": "shared-password"
}
```

**Login Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2023-06-01T18:00:00Z",
  "workstation_id": "front-desk"
}
```

**Protected API Request:**
```
GET /api/jobs
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 5. Security & Accountability

### 5.1 Benefits of the Hybrid Model

- **Operational Simplicity**: Staff don't need to remember individual passwords
- **Accountability**: Every critical action is attributed to a specific staff member
- **Resilience**: Staff turnover doesn't require complex credential management
- **Audit Trail**: Complete history of who did what, when, and from where

### 5.2 Security Considerations

- Workstation passwords should be strong and changed periodically
- Physical access to workstations should be restricted to authorized staff
- JWT secret key should be securely managed and rotated periodically
- Staff should be trained to always select their own name from attribution dropdowns

### 5.3 Comprehensive Audit Trail

Every staff action is logged in the `Event` table with:
- `triggered_by`: The name of the staff member who performed the action
- `workstation_id`: The computer from which the action was performed
- `timestamp`: When the action occurred
- `event_type`: What type of action was performed
- `details`: Additional context about the action

This provides a complete audit trail for compliance, troubleshooting, and accountability. 