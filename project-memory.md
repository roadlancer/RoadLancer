# RoadLancer — Definitive Project Memory & Engineering Brain 🧠

> **Mission:** Eliminate 40–60% intermediary middleman margins in India's commercial trucking industry by directly connecting truck drivers with shippers (personal, business, enterprise) through AI-protected price floors, 5-minute dynamic bidding windows, and double verification (Photo + OTP).

---

## 🏗️ 1. Definitive Architecture & Tech Stack

The platform is structured as a **Docker Compose monolithic suite** splitting compute-heavy AI inference into an isolated FastAPI microservice.

### Frontend Client (`frontend/`)
- **Framework:** Next.js `^15.2.0` (App Router, TypeScript, React 19) deployed as an offline-first **Progressive Web App (PWA)**.
- **Styling & UI:** Tailwind CSS v4 (`@import "tailwindcss";`), shadcn/ui (Radix primitives), HSL CSS variables for sleek dark mode & vibrant light mode.
- **State & Data Fetching:** Zustand v5 (global auth & app state), TanStack Query v5 (server state caching).
- **Localization:** `next-intl` supporting English (`en`) and Hindi (`hi`).
- **Forms & Validation:** React Hook Form + Zod.

### Backend REST API & WebSockets (`backend/`)
- **Core Framework:** Django `>=5.1.6` + Django REST Framework (DRF `>=3.15.2`).
- **Real-Time Engine:** Django Channels `>=4.2.0` powered by **Daphne `>=4.0.0`** ASGI server and Redis channel layer.
- **Authentication:** Phone number + OTP primary auth issuing stateful database sessions stored in Postgres via NextAuth v5 (Auth.js) and Prisma ORM (`Session` table).
- **Async Workers & Scheduling:** Celery `>=5.4.0` + Celery Beat (Redis broker).
- **Database ORM:** PostgreSQL 16 + PostGIS engine (Django DDL owner + Prisma type-safe query client).

### AI & Pricing Microservice (`ai-service/`)
- **Framework:** FastAPI `>=0.110.0` + Pydantic v2 + Uvicorn.
- **ML Engine:** Scikit-learn / XGBoost + NumPy.
- **Endpoints:** `/price-estimate` (calculates fair rate ranges & strict price floors) and `/backhaul-suggest` (geospatial return load matching).

### Infrastructure & External APIs
- **Database Container:** `postgis/postgis:16-3.4` (Port 5432, DB: `roadlancer`, User: `postgres`).
- **Cache & Message Broker:** Redis 7 Alpine (Port 6379, DB 0: Cache/PubSub, DB 1: Celery Broker, DB 2: Celery Results).
- **Payments:** Razorpay API (split payment holding escrow & shipper business subscriptions).
- **Communication:** Exotel API (SMS OTP dispatch & ExoPhone masked calling to prevent disintermediation).

---

## 🛠️ 2. Critical Engineering Patterns & Gotchas (Mandatory AI Context)

### Gotcha A: GDAL / PostGIS Missing on Ubuntu Host OS (Local Dev Fallback)
When running Django directly on a laptop's host OS outside Docker (`uv run uvicorn...`), GDAL C++ libraries (`libgdal.so`) are not installed by default. 
- **Rule:** Do NOT force developers to install 500MB+ GDAL C++ binaries on host OS.
- **Established Pattern:** `backend/config/settings/base.py` implements an automatic `try/except` fallback. If `django.contrib.gis.gdal` cannot be imported, it dynamically downgrades `DATABASES['default']['ENGINE']` from `'django.contrib.gis.db.backends.postgis'` to standard `'django.db.backends.postgresql'`. When running inside Docker containers later, GDAL *is* present (`RUN apt-get install -y gdal-bin`), so PostGIS remains active.

### Gotcha B: pnpm v11 Ignored Build Scripts (`ERR_PNPM_IGNORED_BUILDS`)
In modern `pnpm` v10.6+ / v11 releases, the `"pnpm"` configuration field inside `package.json` is deprecated and ignored. Furthermore, `pnpm install` throws `ERR_PNPM_IGNORED_BUILDS` and aborts with exit code 1 if packages like `esbuild` or `sharp` contain unapproved lifecycle scripts.
- **Established Pattern:** `frontend/.npmrc` sets `ignore-scripts=true`. Additionally, frontend installation commands in Dockerfiles and CI must explicitly pass `pnpm install --ignore-scripts` (or fallback to standard `npm install --ignore-scripts`).

### Gotcha C: Next.js 15 Security Vulnerability Advisory
`next@15.1.8` contains an active security vulnerability warning (`CVE-2025-66478`).
- **Rule:** Always enforce `"next": "^15.2.0"` (or newer patched releases) and matching `"eslint-config-next": "^15.2.0"`.

### Gotcha D: Django Channels Daphne Bootstrapping
For Django Channels real-time WebSockets to intercept ASGI requests properly:
- **Rule:** `'daphne'` MUST be listed as the very first application inside `INSTALLED_APPS` in `base.py`, and `"daphne"` must be explicitly declared in `backend/pyproject.toml`.

### Gotcha E: Real-Time Bidding WebSocket Consumer Pattern (Context7 Verified)
When implementing live bidding consumers in Phase 1:
```python
class BiddingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.shipment_id = self.scope['url_route']['kwargs']['shipment_id']
        self.group_name = f"shipment_{self.shipment_id}_bids"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Broadcast handler
    async def bid_updated(self, event):
        await self.send(text_data=json.dumps(event['data']))
```

---

## 🚦 3. Current Implementation Phase Status

### Phase 0 — Project Setup & Foundation: **COMPLETED ✅**
- Repository scaffolding, `.gitignore`, `.env` configuration, `README.md`, `docker-compose.yml`.
- Shared `core` Django app with abstract `TimeStampedModel`.
- Next.js 15 App Router landing page with rich modern UI aesthetics.
- FastAPI AI microservice live health check verified on `http://localhost:8001/`.
- Django 5 REST API & Admin login verified live on `http://localhost:8000/admin/`.
- Next.js 15 PWA running live on `http://localhost:3000/`.

### Phase 1 — MVP Core Marketplace Loop: **NEXT UP 🎯**
1. **Accounts App:** User models (Driver, Personal/Business/Enterprise Shipper), OTP Redis generation, Exotel SMS integration, SimpleJWT login API.
2. **Shipments App:** Shipment models, Google Maps distance matrix auto-calculation, AI price floor REST integration.
3. **Bidding App:** Bid placement CRUD, countdown timer sync, Celery window expiry winner selection task, Django Channels WebSocket broadcast.
4. **Verification App:** 4-digit pickup & delivery OTP generation, camera photo upload to S3.
5. **Payments App:** Razorpay order creation escrow hold & release payout Celery Beat task.

---

## 📂 4. Core Reference Artifacts
- **[project-scope.md](./project-scope.md):** Detailed product mechanics, user tiers, shipment lifecycle, penalty logic.
- **[tech-stack.md](./tech-stack.md):** Deep engineering rationale for library choices.
- **[implementation-plan.md](./implementation-plan.md):** ~240 atomic engineering tasks categorized across 4 phases.
