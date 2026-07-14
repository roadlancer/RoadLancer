# RoadLancer — Project Memory

> **Mission:** Eliminate intermediary margins in India's trucking industry by connecting drivers with shippers through AI-powered fair pricing and transparent bidding.

> **Scope:** College-level project — simplified features, no enterprise integrations.

---

## Architecture

Three-service architecture: **FastAPI** (Python) for business logic, **Better Auth** (Bun) for authentication, **Vue.js 3** for frontend. All sharing a single PostgreSQL database.

### Backend (FastAPI)
- **Framework:** FastAPI (Python 3.12+)
- **ORM:** Prisma (`prisma-client-py` v0.15.0)
- **Auth:** Session-based via Bearer token → DB lookup (not JWT)
- **Port:** 8000

### Auth Server (Better Auth)
- **Runtime:** Bun (native `Bun.serve` for HTTP)
- **Auth Library:** Better Auth (TypeScript)
- **Database:** Prisma adapter (same PostgreSQL)
- **Port:** 3000

### Frontend (Vue.js)
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS 4
- **Port:** 5173

---

## Default Accounts

| Role | Email | Notes |
|------|-------|-------|
| Admin | admin@roadlancer.com | `isSupreme=true` |
| Driver | driver@roadlancer.com | |
| Shipper | shipper@roadlancer.com | |
| Agent | john@roadlancer.com | `role: admin`, `isSupreme=false` |

> **Note:** All passwords and API keys are stored in Railway environment variables, NOT in code.

---

## Environment Variables

| Variable | Location | Description |
|----------|----------|-------------|
| `DATABASE_URL` | `.env` | PostgreSQL connection string (local or Railway) |
| `BETTER_AUTH_SECRET` | `.env` | Secret key for Better Auth |
| `BETTER_AUTH_URL` | `.env` | Auth server URL |
| `GEMINI_API_KEY` | Railway env vars | Gemini API key for AI features |
| `SMTP_EMAIL` | `.env` | Gmail SMTP email for outbound |
| `SMTP_APP_PASSWORD` | `.env` | Gmail App Password for SMTP |
| `RESEND_API_KEY` | `.env` | Resend API key for fallback email |
| `RESEND_WEBHOOK_SECRET` | `.env` | Resend webhook signature secret |
| `GMAIL_TOKEN_JSON` | Railway env vars | Gmail API OAuth2 token JSON |
| `GMAIL_USER_EMAIL` | Railway env vars | Gmail user email for API access |

---

## Railway Deployment

### Services
| Service | Port | Description |
|---------|------|-------------|
| Backend | 8000 | FastAPI Python backend |
| Auth Server | 3000 | Better Auth + pg-boss |
| Frontend | 4173 | Vue.js SPA |

### Dockerfiles
- **Backend:** Python 3.13 + Node.js 20 + Prisma generate
- **Auth Server:** Bun runtime
- **Frontend:** Multi-stage build with Vite

---

## Email Integration

### Inbound (Customer Email → Support Ticket)
- Google Apps Script forwards emails from `support.roadlancer@gmail.com` to `/api/support/inbound-email` webhook
- **Only registered users' emails are accepted** (validated against user table)
- Backend validates sender email exists in user table
- Creates `support_tickets` record with email threading headers
- Webhook secret validation (`x-webhook-secret` header) for production security

### Outbound (Admin Reply → Customer Email)
- Admin replies via `POST /api/support/admin/{ticket_id}/replies`
- Backend validates recipient email exists in user table
- Sends email via Gmail API with proper threading (In-Reply-To, References headers)
- Falls back to Resend API if Gmail API fails

### AI Auto-Resolution Email Notifications
- pg-boss worker processes tickets asynchronously
- AI agent auto-resolves simple tickets and sends email notification
- Auth server calls backend `/notify-email` endpoint (synchronous)
- Email sent with proper threading headers (In-Reply-To, References)
- All replies come from `support.roadlancer@gmail.com` (single sender address)

### Email Threading
- `in_reply_to` and `email_references` columns on `support_tickets` table
- Column renamed from `references` to `email_references` (PostgreSQL reserved keyword fix)
- Gmail Apps Script captures `In-Reply-To` and `References` headers from incoming emails
- Admin/AI replies use these headers for proper email threading
- Thread headers stored and used for all outbound emails

### Email Security
- Only registered users can create tickets via email (inbound validation)
- Only registered users receive replies (outbound validation)
- Git history cleaned to remove leaked credentials
- All secrets stored in Railway environment variables only

---

## Testing

- **Framework:** Vitest + @testing-library/vue for component tests
- **E2E:** Playwright for critical full-stack flows only
- **Test location:** `frontend/src/**/*.spec.ts`
- **Run tests:** `bunx vitest run` (from frontend/ directory)

---

## Security Notes

### Credential Management
- All API keys, passwords, and secrets stored in Railway environment variables
- No hardcoded credentials in source code
- Git history cleaned with `git-filter-repo` to remove leaked credentials
- `.env` files are `.gitignore`d and never committed

### Production Security
- Webhook endpoints require `x-webhook-secret` header for authentication
- Email validation ensures only registered users can create/receive tickets
- Session-based auth via Bearer token (not JWT)
