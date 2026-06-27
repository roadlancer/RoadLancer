# RoadLancer — Project Memory & Engineering Brain 🧠

> **Mission:** Eliminate 40–60% intermediary middleman margins in India's commercial trucking industry by directly connecting truck drivers with shippers (personal, business, enterprise) through AI-protected price floors, dynamic bidding windows, and double verification (Photo + OTP).

---

## 🏗️ 1. Architecture & Tech Stack

The platform is a **Laravel monolith** serving Blade templates with embedded Vue.js 3 components, plus an isolated FastAPI microservice for compute-heavy AI inference.

### Laravel Monolith (Backend + Frontend)
- **Framework:** Laravel 12 (PHP 8.2+), Eloquent ORM, Blade templates.
- **Frontend Components:** Vue.js 3 (Composition API) embedded in Blade via Vite, Tailwind CSS 4.
- **Authentication:** Laravel native session auth — email/password, bcrypt hashing, database `sessions` table.
- **Queue & Scheduling:** Laravel Queue (Redis driver) + Task Scheduling (replaces Celery).
- **Real-Time:** Laravel Reverb (WebSocket bidding updates & GPS streaming).
- **Database:** PostgreSQL 16 + PostGIS (Eloquent ORM + geospatial queries).
- **Cache & Broker:** Redis 7 (cache, queue broker, session driver).

### AI & Pricing Microservice (`ai-service/`)
- **Framework:** FastAPI `>=0.110.0` + Pydantic v2 + Uvicorn.
- **ML Engine:** Scikit-learn / XGBoost + NumPy.
- **Endpoints:** `/price-estimate` (fair rate ranges & strict price floors) and `/backhaul-suggest` (geospatial return load matching).

### Infrastructure & External APIs
- **Database:** PostgreSQL 16 + PostGIS (Port 5432, DB: `roadlancer`, User: `postgres`).
- **Cache & Message Broker:** Redis 7 Alpine (Port 6379).
- **Payments:** Razorpay API (split payment escrow & business subscriptions).
- **Communication:** Exotel API (SMS OTP dispatch & ExoPhone masked calling).

---

## 🛠️ 2. Engineering Patterns & Key Decisions

### Decision A: Laravel Monolith over Decoupled SPA
We chose a Laravel + Blade + Vue monolith over a decoupled API + SPA architecture for:
- **Simplified deployment** — Single application serves HTML, API, and WebSockets.
- **Built-in batteries** — Auth, queues, scheduling, broadcasting, file storage ship natively in Laravel.
- **SEO-friendly** — Server-rendered Blade templates with Vue components for interactivity where needed.

### Decision B: Laravel Native Auth over Better Auth
Better Auth is a Node.js/TypeScript library. In a PHP monolith, it would require running a separate Node.js sidecar process. Laravel's built-in session authentication with bcrypt hashing is the natural, zero-dependency choice.

### Decision C: Laravel Queue replaces Celery
Laravel Queue with Redis driver provides the same async job processing and scheduled task capabilities as Celery + Celery Beat, but natively integrated with the Eloquent ORM and Laravel ecosystem.

---

## 🚦 3. Current Implementation Phase Status

### Phase 0 — Project Setup & Foundation: **IN PROGRESS 🔄**
- ✅ Project scope defined (`project-scope.md`)
- ✅ Tech stack documented (`tech-stack.md`)
- ✅ Implementation plan written (`implementation-plan.md`)
- ✅ FastAPI AI microservice live on `http://localhost:8001/`
- ✅ PostgreSQL & Redis running via Docker Compose
- 🔄 Laravel scaffolding (pending `composer create-project`)
- 🔄 Vue.js 3 + Vite integration
- 🔄 Docker Compose update for Laravel services

### Phase 1 — MVP Core Marketplace Loop: **NEXT UP 🎯**
1. **Auth:** User registration/login (email/password), role-based middleware (Driver, Shipper tiers).
2. **Shipments:** Eloquent models, Google Maps distance calculation, AI price floor API integration.
3. **Bidding:** Bid CRUD, countdown timer sync, Queue job for window expiry, Reverb WebSocket broadcast.
4. **Verification:** 4-digit pickup & delivery OTP, camera photo upload to S3.
5. **Payments:** Razorpay order creation, escrow hold & release payout Queue job.

---

## 📂 4. Core Reference Artifacts
- **[project-scope.md](./project-scope.md):** Detailed product mechanics, user tiers, shipment lifecycle, penalty logic.
- **[tech-stack.md](./tech-stack.md):** Deep engineering rationale for library choices.
- **[implementation-plan.md](./implementation-plan.md):** Engineering tasks categorized across phases.
