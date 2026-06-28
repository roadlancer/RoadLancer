# RoadLancer — Project Memory 🧠

> **Mission:** Eliminate intermediary margins in India's trucking industry by connecting drivers with shippers through AI-powered fair pricing and transparent bidding.

> **Scope:** College-level project — simplified features, no enterprise integrations.

---

## 🏗️ 1. Architecture

Three-service architecture: **FastAPI** (Python) for business logic, **Better Auth** (Node.js) for authentication, **Vue.js 3** for frontend. All sharing a single PostgreSQL database.

### Backend (FastAPI)
- **Framework:** FastAPI (Python 3.12+)
- **ORM:** Prisma (`prisma-client-py`)
- **Auth:** JWT verification via `fastapi-betterauth`
- **AI Pricing:** scikit-learn, numpy (bundled in same service)
- **Port:** 8000

### Auth Server (Better Auth)
- **Runtime:** Node.js 20+
- **Auth Library:** Better Auth (TypeScript)
- **Database:** Prisma adapter (same PostgreSQL)
- **Features:** Registration, login, sessions, JWT, role-based access
- **Port:** 3000

### Frontend (Vue.js)
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS 4
- **Auth Client:** `@better-auth/vue`
- **Port:** 5173

---

## 🛠️ 2. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth | Better Auth (Node.js) | Production-ready, JWT, role-based, great DX |
| Backend | FastAPI (Python) | Modern, async, auto-docs, good for AI integration |
| ORM | Prisma | Type-safe, migrations, works with both Node.js and Python |
| Database | PostgreSQL 16 | Standard SQL, no PostGIS |
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
| Phase 1 | Project Restructure (Laravel → FastAPI + Better Auth) | 🔄 In Progress |
| Phase 2 | Better Auth Server Setup | ⬜ Not Started |
| Phase 3 | FastAPI Backend Setup | ⬜ Not Started |
| Phase 4 | Vue.js Frontend Setup | ⬜ Not Started |
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
