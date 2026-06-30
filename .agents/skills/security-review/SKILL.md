---
name: security-review
description: Review the RoadLancer codebase for security vulnerabilities. Use when users mention security audit, vulnerability scan, security review, or need to check for common web application security issues.
---

# Security Vulnerability Review

Systematic security audit for RoadLancer (FastAPI + Better Auth + Vue.js 3 + PostgreSQL).

---

## Review Checklist

### 1. Authentication & Session Security

**Check: `auth-server/auth.ts`**
- [ ] `BETTER_AUTH_SECRET` is strong (min 32 chars, random)
- [ ] `trustedOrigins` is restrictive (no wildcards in production)
- [ ] Session expiry is reasonable (7 days max)
- [ ] `useSecureCookies` enabled in production
- [ ] No `disableCSRFCheck: true` in production
- [ ] No `disableOriginCheck: true` in production

**Check: `frontend/src/lib/auth-client.ts`**
- [ ] `baseURL` is correct (empty for proxy, not exposed)
- [ ] No hardcoded secrets in client code

**Check: `frontend/src/composables/useAuth.ts`**
- [ ] Session data not stored in localStorage
- [ ] Sign-out clears all state properly

### 2. Authorization & Access Control

**Check: `backend/app/routes/auth.py`**
- [ ] `get_current_user()` validates session token expiry
- [ ] User role checked on protected endpoints
- [ ] No IDOR (Insecure Direct Object References) — users can't access other users' data

**Check: `backend/app/routes/shipments.py`**
- [ ] Shipment operations verify ownership (driver can only bid on assigned shipments)
- [ ] Shipper can only manage their own shipments
- [ ] No horizontal privilege escalation

**Check: `frontend/src/router/index.ts`**
- [ ] `meta.requiresAuth` on protected routes
- [ ] `meta.role` guards prevent cross-role access
- [ ] Guest-only routes redirect authenticated users

### 3. Input Validation & Sanitization

**Check: FastAPI Pydantic models**
- [ ] All inputs validated with Pydantic models
- [ ] String length limits enforced
- [ ] Numeric ranges validated
- [ ] Email format validated
- [ ] No raw SQL queries (use Prisma)

**Check: Frontend forms**
- [ ] Zod validation on all inputs
- [ ] Client-side validation doesn't replace server-side
- [ ] No `v-html` with user content (XSS risk)

### 4. SQL Injection & ORM Safety

**Check: `backend/app/routes/`**
- [ ] No raw SQL with string interpolation
- [ ] Prisma queries use parameterized values
- [ ] No `execute_raw` with user input

### 5. Cross-Site Scripting (XSS)

**Check: Frontend**
- [ ] No `v-html` directive with dynamic content
- [ ] No `innerHTML` assignments
- [ ] User data rendered with `{{ }}` (auto-escaped)
- [ ] No `dangerouslySetInnerHTML` equivalent

### 6. Cross-Site Request Forgery (CSRF)

**Check: Auth server**
- [ ] CSRF protection enabled (default in Better Auth)
- [ ] `trustedOrigins` matches frontend URL exactly
- [ ] No `disableCSRFCheck: true`

### 7. Rate Limiting & Brute Force

**Check: `backend/app/middleware.py`**
- [ ] Rate limiting active (60 req/min/IP)
- [ ] Login endpoint has additional rate limiting
- [ ] No bypass via IP header manipulation

**Check: `auth-server/auth.ts`**
- [ ] Better Auth rate limiting configured
- [ ] Max login attempts enforced

### 8. Sensitive Data Exposure

**Check: Environment files**
- [ ] `.env` files in `.gitignore`
- [ ] No secrets in `package.json` or `pyproject.toml`
- [ ] `DATABASE_URL` not logged
- [ ] `BETTER_AUTH_SECRET` not logged

**Check: API responses**
- [ ] Password hashes never returned
- [ ] Session tokens not in URLs
- [ ] Error messages don't leak internals

**Check: Frontend**
- [ ] No API keys in client bundle
- [ ] No secrets in `localStorage` or `sessionStorage`

### 9. Dependency Security

**Check: `auth-server/package.json`**
- [ ] No known vulnerable packages
- [ ] Dependencies pinned to specific versions

**Check: `frontend/package.json`**
- [ ] No known vulnerable packages
- [ ] No deprecated packages

**Check: `backend/pyproject.toml`**
- [ ] No known vulnerable packages
- [ ] Python version compatible

### 10. CORS Configuration

**Check: `backend/app/main.py`**
- [ ] `allow_origins` is restrictive (not `["*"]`)
- [ ] `allow_credentials: true` with specific origins
- [ ] No `allow_methods: ["*"]` in production

### 11. Error Handling

**Check: Backend**
- [ ] No stack traces returned to client
- [ ] Generic error messages for auth failures
- [ ] Detailed errors only in server logs

**Check: Frontend**
- [ ] Auth errors don't reveal user existence
- [ ] Form errors are generic ("Invalid credentials")

### 12. Session Security

**Check: Database sessions**
- [ ] Session tokens are opaque (not predictable)
- [ ] Sessions expire properly
- [ ] Old sessions cleaned up
- [ ] Sign-out invalidates session in DB

---

## How to Run

1. Read each file mentioned in the checklist
2. Verify each item is passing or flag as vulnerability
3. Assign severity: **Critical**, **High**, **Medium**, **Low**, **Info**
4. Provide fix recommendation for each issue found

---

## Output Format

```markdown
## Security Review — [Date]

### Summary
- Critical: X
- High: X
- Medium: X
- Low: X
- Info: X

### Findings

#### [SEVERITY] Finding Title
- **File:** `path/to/file.ts:line`
- **Description:** What the issue is
- **Impact:** What could happen
- **Recommendation:** How to fix
```

---

## Common Vulnerabilities in This Stack

| Vulnerability | Where to Check |
|---------------|----------------|
| Weak password policy | `auth-server/auth.ts` → `emailAndPassword` |
| Session fixation | `auth-server/auth.ts` → `session` config |
| IDOR | `backend/app/routes/` → ownership checks |
| SQL injection | `backend/app/routes/` → Prisma queries |
| XSS | `frontend/src/` → `v-html`, `innerHTML` |
| CSRF | `auth-server/auth.ts` → `trustedOrigins` |
| Open redirect | Login success redirect URL |
| Information disclosure | Error messages, API responses |
| Missing rate limiting | `backend/app/middleware.py` |
| Insecure dependencies | `package.json`, `pyproject.toml` |
