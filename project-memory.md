# RoadLancer — Project Memory 🧠

> **Mission:** Eliminate intermediary margins in India's trucking industry by connecting drivers with shippers through AI-powered fair pricing and transparent bidding.

> **Scope:** College-level project — simplified features, no enterprise integrations.

---

## 🏗️ 1. Architecture

Simple **Laravel monolith** serving Blade templates with embedded Vue.js 3 components, plus a lightweight FastAPI microservice for AI price calculations.

### Laravel Monolith
- **Framework:** Laravel 12 (PHP 8.2+), Eloquent ORM, Blade templates.
- **Frontend:** Vue.js 3 components embedded in Blade via Vite, Tailwind CSS 4.
- **Auth:** Laravel native session auth — email/password, bcrypt, database sessions.
- **Database:** PostgreSQL 16 (standard, no PostGIS).
- **Cache:** File driver (no Redis).
- **Queue:** Sync driver (no workers needed).

### AI Microservice (`ai-service/`)
- **Framework:** FastAPI + Pydantic v2 + Uvicorn.
- **Endpoints:** `/price-estimate` (deterministic pricing formula, no ML model yet).

---

## 🛠️ 2. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth | Laravel native sessions | Zero dependencies, built-in, perfect for monolith |
| Database | PostgreSQL (no PostGIS) | Standard SQL, no geospatial C++ library dependencies |
| Cache | File driver | No Redis setup needed for local dev |
| Queue | Sync driver | Jobs run immediately, no worker process to manage |
| Real-time | AJAX polling (5s interval) | No WebSocket complexity for college demo |
| Payments | Mock (no Razorpay) | Status fields only, no real payment processing |
| SMS/OTP | Mock (displayed on screen) | No Exotel integration, OTP shown in dashboard |
| Docker | Optional | App runs directly with `php artisan serve` |

---

## 🚦 3. Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Project Setup (Laravel + Vue + AI service) | 🔄 In Progress |
| Phase 1 | Auth & User Management | ⬜ Not Started |
| Phase 2 | Shipments & AI Pricing | ⬜ Not Started |
| Phase 3 | Bidding System | ⬜ Not Started |
| Phase 4 | Verification & Completion | ⬜ Not Started |
| Phase 5 | Admin Panel & Analytics | ⬜ Not Started |
| Phase 6 | Polish & Presentation | ⬜ Not Started |

---

## 📂 4. Reference Files
- **[project-scope.md](./project-scope.md):** Features, database schema, API endpoints.
- **[tech-stack.md](./tech-stack.md):** Technology choices with rationale.
- **[implementation-plan.md](./implementation-plan.md):** Phase-by-phase task checklist.
