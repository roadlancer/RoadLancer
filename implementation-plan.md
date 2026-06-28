# RoadLancer — Implementation Plan

> **References:** [project-scope.md](./project-scope.md) · [tech-stack.md](./tech-stack.md)

---

## Phase 0 — Project Setup ✅

> **Goal:** Get the development environment running locally.

- [x] Install PHP 8.2+ with extensions
- [x] Install Composer 2.x
- [x] Install Node.js 20+ and npm
- [x] Install PostgreSQL 16 (local, port 5433)
- [x] Install Python 3.12+ and `uv`
- [x] Create PostgreSQL database: `roadlancer` (user: `postgres`, password: `postgres`)

---

## Phase 1 — Project Restructure 🔄

> **Goal:** Remove Laravel, set up new three-service architecture.

- [x] Remove Laravel files (app/, routes/, resources/, config/, database/, vendor/, composer.json, artisan, etc.)
- [x] Create `frontend/`, `auth-server/`, `backend/` directories
- [x] Update tech-stack.md and project-memory.md
- [ ] Update project-scope.md if needed
- [ ] Clean up git history (optional)

---

## Phase 2 — Better Auth Server (`auth-server/`)

> **Goal:** Working auth server with registration, login, JWT.

### 2.1 Setup
- [ ] Initialize Node.js project: `npm init -y`
- [ ] Install dependencies: `better-auth`, `@better-auth/prisma-adapter`, `prisma`, `@prisma/client`
- [ ] Initialize Prisma: `npx prisma init`
- [ ] Configure Prisma schema (auth tables only)
- [ ] Set up `.env` with `DATABASE_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`

### 2.2 Auth Configuration
- [ ] Create `auth.ts` with Better Auth config
- [ ] Enable email/password authentication
- [ ] Enable JWT plugin (for FastAPI verification)
- [ ] Add custom user fields: `role` (driver/shipper/admin), `phone`
- [ ] Configure role-based access

### 2.3 Routes
- [ ] Create route handler (`/api/auth/*`)
- [ ] Set up CORS for frontend (port 5173)
- [ ] Verify: `GET /api/auth/ok` returns `{ status: "ok" }`

### 2.4 Seed Data
- [ ] Seed admin user: `admin@roadlancer.com` / `admin123`
- [ ] Seed driver user: `driver@roadlancer.com` / `driver123`
- [ ] Seed shipper user: `shipper@roadlancer.com` / `shipper123`

### 2.5 Run
- [ ] Start server: `node server.js` (port 3000)

---

## Phase 3 — FastAPI Backend (`backend/`)

> **Goal:** Working API server with shipment CRUD, AI pricing, JWT verification.

### 3.1 Setup
- [ ] Initialize Python project with `uv`
- [ ] Install dependencies: `fastapi`, `uvicorn`, `prisma`, `fastapi-betterauth`, `pydantic`, `scikit-learn`, `numpy`
- [ ] Set up `.env` with `DATABASE_URL`, `BETTER_AUTH_URL`

### 3.2 Prisma Schema
- [ ] Create `prisma/schema.prisma` with business tables:
  - `shipments` (references `user.id`)
  - `bids` (references `user.id` and `shipments.id`)
  - `verifications` (references `shipments.id`)
- [ ] Run `prisma migrate dev`

### 3.3 Auth Middleware
- [ ] Set up `fastapi-betterauth` dependency
- [ ] Create `get_current_user()` dependency function
- [ ] Protect all API routes with JWT verification

### 3.4 Routes
- [ ] `GET /api/shipments` — list available shipments
- [ ] `POST /api/shipments` — create shipment (shipper only)
- [ ] `GET /api/shipments/{id}` — get shipment details
- [ ] `PUT /api/shipments/{id}/status` — update shipment status
- [ ] `POST /api/shipments/{id}/bids` — place a bid (driver only)
- [ ] `GET /api/shipments/{id}/bids` — list bids for a shipment
- [ ] `PUT /api/bids/{id}/accept` — accept a bid (shipper only)
- [ ] `POST /api/price-estimate` — get AI price estimate

### 3.5 AI Pricing
- [ ] Port existing pricing formula from old ai-service
- [ ] Create `/price-estimate` endpoint
- [ ] Integrate with shipment creation flow

### 3.6 Run
- [ ] Start server: `uvicorn app.main:app --port 8000 --reload`

---

## Phase 4 — Vue.js Frontend (`frontend/`)

> **Goal:** Working SPA with auth pages and role-based dashboards.

### 4.1 Setup
- [ ] Initialize Vue.js 3 project: `npm create vue@latest`
- [ ] Install Tailwind CSS 4
- [ ] Install `@better-auth/vue` client
- [ ] Install `axios` for API calls
- [ ] Configure Vite proxy for API calls

### 4.2 Auth Pages
- [ ] Login page (email + password)
- [ ] Register page (name, email, password, phone, role selection)
- [ ] Auth state management (session, user info)
- [ ] Route guards (redirect based on role)

### 4.3 Layouts
- [ ] App layout with navigation bar
- [ ] Role-based navigation (different menu for driver/shipper/admin)
- [ ] Footer, loading states

### 4.4 Driver Dashboard
- [ ] Available shipments list
- [ ] My bids (pending, accepted, rejected)
- [ ] Active trips
- [ ] Earnings history

### 4.5 Shipper Dashboard
- [ ] Create shipment form (with AI pricing display)
- [ ] My shipments list (with status badges)
- [ ] View bids on my shipments
- [ ] Accept/reject bids

### 4.6 Admin Dashboard
- [ ] User management (list, toggle verification)
- [ ] All shipments list (filter by status)
- [ ] Basic analytics (charts)

---

## Phase 5 — Core Features

> **Goal:** Complete shipment lifecycle with bidding and verification.

### 5.1 Shipment Lifecycle
- [ ] Shipper creates shipment → AI calculates price range
- [ ] Shipment status: `draft` → `active`
- [ ] Drivers browse and bid
- [ ] Shipper accepts bid → status: `assigned`
- [ ] Driver picks up → status: `in_transit`
- [ ] Driver delivers → status: `delivered`
- [ ] Shipper confirms → status: `completed`

### 5.2 Bidding System
- [ ] Place bid (amount >= AI floor price)
- [ ] List bids for a shipment
- [ ] Accept bid (auto-rejects others)
- [ ] Countdown timer (visual, based on `bidding_ends_at`)

### 5.3 OTP Verification
- [ ] Generate 4-digit OTP on shipment assignment
- [ ] Display OTP to shipper on dashboard
- [ ] Driver enters OTP to confirm pickup → `in_transit`
- [ ] Generate new OTP for delivery
- [ ] Shipper enters delivery OTP → `delivered`

### 5.4 AI Price Integration
- [ ] On shipment creation: call FastAPI `/price-estimate`
- [ ] Display AI price range on creation form
- [ ] Validate bids against floor price

---

## Phase 6 — Polish & Presentation

> **Goal:** Make it demo-ready for college submission.

### 6.1 UI Polish
- [ ] Consistent Tailwind styling across all pages
- [ ] Mobile responsive layouts
- [ ] Loading spinners and error states
- [ ] Empty state illustrations ("No shipments yet")
- [ ] Toast notifications for actions

### 6.2 Seed Data
- [ ] Create database seeder with sample users (3 drivers, 2 shippers, 1 admin)
- [ ] Create sample shipments across different statuses
- [ ] Create sample bids on active shipments

### 6.3 Documentation
- [ ] Update README.md with final setup instructions
- [ ] Add screenshots to README
- [ ] Prepare demo script (walkthrough of all features)
- [ ] Create project report / presentation slides
