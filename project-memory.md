# RoadLancer — Project Memory 🧠

> **Mission:** Eliminate intermediary margins in India's trucking industry by connecting drivers with shippers through AI-powered fair pricing and transparent bidding.

> **Scope:** College-level project — simplified features, no enterprise integrations.

---

## 🏗️ 1. Architecture

Three-service architecture: **FastAPI** (Python) for business logic, **Better Auth** (Node.js) for authentication, **Vue.js 3** for frontend. All sharing a single PostgreSQL database.

### Backend (FastAPI)
- **Framework:** FastAPI (Python 3.12+)
- **ORM:** Prisma (`prisma-client-py` v0.15.0)
- **Auth:** Session-based via Bearer token → DB lookup (not JWT)
- **Middleware:** RequestLoggingMiddleware, RateLimitMiddleware (60 req/min/IP)
- **AI Pricing:** scikit-learn, numpy (bundled in same service)
- **Port:** 8000

### Auth Server (Better Auth)
- **Runtime:** Node.js 20+
- **Auth Library:** Better Auth (TypeScript)
- **Database:** Prisma adapter (same PostgreSQL)
- **Prisma:** v7.x — uses `prisma-client` generator, `@prisma/adapter-pg` driver adapter, `tsx`
- **Features:** Registration, login, sessions, role-based access
- **Sessions:** Database sessions + Bearer plugin (opaque tokens, not JWT)
- **Port:** 3000

### Frontend (Vue.js)
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS 4
- **UI Library:** shadcn-vue (reka-ui primitives, Lucide icons via `@lucide/vue`)
- **Theme:** Teal (primary: `oklch(0.511 0.096 186.391)`)
- **Form Validation:** Zod v4 + manual `safeParse()` (no vuehookform)
- **Auth Client:** `better-auth` vanilla client (`baseURL: ''` for Vite proxy)
- **Router:** Vue Router with auth navigation guards
- **Components:** Button, Input, Label, Card, Avatar, Badge, Separator, Tabs, Checkbox, Alert, RadioGroup
- **Layout:** Sticky NavBar, Footer, centered login card with role selection
- **Port:** 5173

---

## 🛠️ 2. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth | Better Auth (Node.js) | Production-ready, role-based, great DX |
| Backend | FastAPI (Python) | Modern, async, auto-docs, good for AI integration |
| ORM | Prisma | Type-safe, migrations, works with both Node.js and Python |
| Database | PostgreSQL 16 | Standard SQL, no PostGIS |
| Session Type | Database + Bearer | Opaque tokens verified via DB lookup, not JWT |
| UI Library | shadcn-vue | Accessible, themeable, Tailwind-native components |
| Theme | Teal | Blue-green accent for transportation/logistics branding |
| Form Validation | Zod + manual | `@vuehookform/core` incompatible with Zod v4 runtime |
| Auth Client | `better-auth` vanilla | `@better-auth/vue` removed; singleton composable pattern |
| User Roles | driver, shipper only | Admin removed for simplicity — college-level project |
| Cache | File driver | No Redis needed for local dev |
| Queue | Sync driver | Jobs run immediately, no worker process |
| Real-time | AJAX polling (5s) | No WebSocket complexity |
| Payments | Mock | Status fields only |
| SMS/OTP | Mock | Displayed on screen, no Exotel |
| Docker | No | Runs directly on laptop |

---

## 🚦 3. Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Project Setup | ✅ Complete |
| Phase 1 | Project Restructure (Laravel → FastAPI + Better Auth) | ✅ Complete |
| Phase 2 | Better Auth Server Setup | ✅ Complete |
| Phase 3 | FastAPI Backend Setup | ✅ Complete |
| Phase 4 | Vue.js Frontend Setup (Login, NavBar, Home, Footer) | ✅ Complete |
| Phase 5 | Core Features (shipments, bids, verification) | ⬜ Not Started |
| Phase 6 | Polish & Presentation | ⬜ Not Started |

---

## 📂 4. Reference Files

- **[project-scope.md](./project-scope.md):** Features, database schema, API endpoints.
- **[tech-stack.md](./tech-stack.md):** Technology choices with rationale.
- **[implementation-plan.md](./implementation-plan.md):** Phase-by-phase task checklist.

---

## 🔌 5. Service Ports

| Service | Port | URL |
|---------|------|-----|
| Vue.js Frontend | 5173 | http://localhost:5173 |
| Better Auth Server | 3000 | http://localhost:3000 |
| FastAPI Backend | 8000 | http://localhost:8000 |
| PostgreSQL | 5433 | localhost:5433 |

---

## 🔐 6. Authentication System

### Overview
Authentication uses **Better Auth** (Node.js) for session management and **FastAPI** (Python) for session verification via database lookup. Sessions are **database-backed** with opaque Bearer tokens — not JWT.

### Auth Flow
```
Vue Frontend (5173)
  ↓ User selects role (driver/shipper)
  ↓ signIn.email({ email, password, name: role })
  ↓ → Vite proxy → localhost:3000/api/auth/sign-in/email
Better Auth Server (3000)
  ↓ Validates credentials against PostgreSQL
  ↓ Creates session record with opaque token
  ↓ Returns { token, user: { id, name, email, role, phone } }
  ↓ Sets HttpOnly session cookie
Frontend receives response
  ↓ Stores token via authClient.getSession() (reads cookie)
  ↓ useAuth() composable holds user state globally
  ↓ router.push('/') → NavBar shows role-based dashboard link
```

### Session Verification (FastAPI Backend)
```
Frontend sends: Authorization: Bearer <session_token>
  ↓
FastAPI dependency: get_current_user()
  ↓ Looks up session.token in DB
  ↓ Checks session.expiresAt > now
  ↓ Looks up user by session.userId
  ↓ Returns { id, email, name, role, phone }
```

### Database Schema (Auth Tables)
| Table | Purpose |
|-------|---------|
| `user` | id, name, email, emailVerified, image, role (enum), phone |
| `session` | id, token (unique), expiresAt, userId, ipAddress, userAgent |
| `account` | OAuth provider accounts (not used for email/password) |
| `verification` | Email verification tokens |

### Role System
- **Enum:** `driver` | `shipper` (admin removed for simplicity)
- **Default:** `driver`
- **Stored as:** Prisma enum in DB, string array in Better Auth config (`type: ["driver", "shipper"]`)
- **Access:** `user.role` available in frontend after `fetchSession()`
- **Login:** User selects role via radio buttons before signing in

### Frontend Auth Implementation
- **Client:** `better-auth/vue` `createAuthClient({ baseURL: '' })` — empty baseURL for Vite proxy
- **Composable:** `useAuth()` — singleton pattern (lazy-init), provides `user`, `loading`, `fetchSession()`, `signOut()`
- **Router:** Vue Router with auth navigation guards (`beforeEach`)
  - `meta.requiresAuth` → redirects to `/login` if not authenticated
  - `meta.guest` → redirects to `/` if already authenticated
  - `meta.role` → redirects to `/` if user role doesn't match
- **Login:** Role radio buttons → `signIn.email()` → `fetchSession()` → validates `user.role` against selected role → `router.push('/driver'|'/shipper')` → if mismatch: generic error + sign out
- **Sign out:** `authClient.signOut()` → clears user → `window.location.href = '/login'`

### Backend Auth Implementation
- **Dependency:** `get_current_user(authorization: Header)` — extracts Bearer token
- **Verification:** DB lookup on `session` table → expiry check → user lookup
- **Protected routes:** `user: dict = Depends(get_current_user)` in FastAPI

### Backend Middleware
- **RequestLoggingMiddleware:** Logs `METHOD /path → status (duration)` for every request
- **RateLimitMiddleware:** 60 requests per IP per 60 seconds, returns 429 if exceeded
- **CORSMiddleware:** Allows `http://localhost:5173` with credentials

### Environment Variables
| Variable | Location | Value |
|----------|----------|-------|
| `DATABASE_URL` | `.env` (root) | `postgresql://postgres:postgres@localhost:5433/roadlancer` |
| `BETTER_AUTH_SECRET` | `.env` (root) | Random secret for session signing |
| `BETTER_AUTH_URL` | `.env` (auth-server) | `http://localhost:3000` |
| `TRUSTED_ORIGINS` | `.env` (root) | `http://localhost:5173` |

### Session Configuration
- **Expiry:** 7 days (`60 * 60 * 24 * 7`)
- **Update age:** 1 day (`60 * 60 * 24`) — refreshes if session is active
- **Token:** Opaque string, stored in `session.token` column

---

## 🎨 7. UI Components & Layout

### shadcn-vue Components Installed
| Component | Purpose |
|-----------|---------|
| Button | Primary actions, social login |
| Input | Email, phone, password fields |
| Label | Form field labels |
| Card | Login card, home dashboard cards |
| Avatar | User avatar with fallback |
| Badge | Role display |
| Separator | Visual dividers |
| Tabs | Email/phone login switcher |
| Checkbox | Remember me |
| Alert | Error messages |
| RadioGroup | Role selection (driver/shipper) |

### Layout Structure
- **App.vue:** `min-h-screen flex flex-col bg-background` → NavBar → `<main class="flex-1">` → Footer
- **NavBar:** Sticky (`sticky top-0 z-50 backdrop-blur-md`), role-based dashboard link, sign out button, Sign in button uses default primary teal background
- **Footer:** Brand, 3 link columns (Product, Company, Legal), social icons, copyright
- **Login:** Centered card with role radio buttons, tabs (email/phone), social login

### Theme (Teal)
- **Primary:** `oklch(0.511 0.096 186.391)` — teal blue-green
- **Primary Foreground:** `oklch(0.984 0.014 180.72)` — light teal tint
- **Charts:** Teal gradient palette (chart-1 through chart-5)
- **Dark mode:** Supported via `.dark` class

### Pages
| Route | Component | Access |
|-------|-----------|--------|
| `/` | HomeView | All authenticated users |
| `/login` | LoginView | Guest only |
| `/driver` | DriverDashboard | Driver only |
| `/shipper` | ShipperDashboard | Shipper only |

---

## 🔑 8. Default Accounts

| Role | Email | Password |
|------|-------|----------|
| Driver | driver@roadlancer.com | driver123 |
| Shipper | shipper@roadlancer.com | shipper123 |

> **Note:** Only these two accounts should exist. Old admin/test users must be deleted from DB if found.

---

## ⚠️ 9. Known Issues & Workarounds

- **Prisma 7 (auth-server):** Requires `prisma-client` generator (not `prisma-client-js`), driver adapter (`@prisma/adapter-pg`), no `url` in schema (URL in `prisma.config.ts`)
- **Python Prisma (`prisma-client-py`):** Still requires `url` in schema
- **`@vuehookform/core`:** Incompatible with Zod v4 — `extractSubSchema` traverses `_def.checks` causing runtime crashes. Use manual `safeParse()` instead
- **Better Auth enum workaround:** `type: ["driver", "shipper"]` in `additionalFields`
- **HttpOnly cookies:** Can't read in JS — removed router guards, auth composable handles all state
- **Backend `pyproject.toml`:** Missing `[tool.setuptools.packages]` — `pip install -e .` broken; install deps individually
- **Chrome autofill:** Use `autocomplete="new-password"` on inputs to prevent yellow background
- **Auth server startup:** Must use `setsid` (not `< /dev/null`) to keep Hono alive — `process.stdin.resume()` fails when stdin is redirected
- **Vite cache:** Clear `node_modules/.vite` when changing imports (e.g., lucide-vue-next → @lucide/vue)
- **TypeScript schema indexing:** Cast `schema.shape` to `Record<string, any>` when indexing with string
- **Login role validation:** After `fetchSession()`, compare `user.role` with selected role — mismatch shows generic "Invalid credentials" error (never reveals actual role for security)
- **Old admin user:** If old admin user exists with role `driver`, login succeeds with driver radio button — delete stale users from DB
- **Seed users must have passwords:** Users created via Prisma directly have no password hash — always register via `/api/auth/sign-up/email` endpoint

---

## 📁 10. Key Files

| File | Purpose |
|------|---------|
| `auth-server/auth.ts` | Better Auth config — trusted origins, Bearer plugin, role enum |
| `auth-server/server.ts` | Hono server (port 3000) |
| `auth-server/prisma/schema.prisma` | Auth schema — enum Role, user/session/account/verification |
| `auth-server/seed.ts` | Database seeder — driver and shipper users |
| `backend/app/main.py` | FastAPI app with CORS, logging, rate limit middleware |
| `backend/app/middleware.py` | RequestLoggingMiddleware, RateLimitMiddleware |
| `backend/app/routes/auth.py` | Session-based auth via Bearer token → DB lookup |
| `backend/app/routes/shipments.py` | Shipment CRUD + bid routes |
| `frontend/src/style.css` | Tailwind v4 + shadcn teal theme + autofill overrides |
| `frontend/src/router/index.ts` | Vue Router with auth + role navigation guards |
| `frontend/src/composables/useAuth.ts` | Singleton composable — exports `user`, `loading`, `fetchSession` |
| `frontend/src/components/NavBar.vue` | Sticky nav — role dashboard link, sign out |
| `frontend/src/components/Footer.vue` | Brand, links, social icons, copyright |
| `frontend/src/views/LoginView.vue` | Role radio buttons, tabs, social login, Zod validation |
| `frontend/src/views/HomeView.vue` | Dashboard — avatar, role badge, info cards |
| `frontend/src/views/DriverDashboard.vue` | Driver-only page |
| `frontend/src/views/ShipperDashboard.vue` | Shipper-only page |
