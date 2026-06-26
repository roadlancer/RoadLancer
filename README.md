# RoadLancer 🚛

**AI-Powered Transportation Management & Direct Trucking Marketplace for India**

RoadLancer eliminates 40-60% middleman margins in India's trucking industry by connecting drivers directly with shippers (personal, business, enterprise) through AI-enforced price floors, transparent 5-minute bidding windows, and double verification (Photo + OTP).

---

## 🏗️ Tech Stack

- **Frontend:** Next.js 15 (App Router, TypeScript, Tailwind CSS v4, shadcn/ui, Zustand, TanStack Query, next-intl) deployed as a PWA
- **Backend API:** Django 5 + Django REST Framework (DRF, JWT auth, django-phonenumber-field)
- **Real-Time:** Django Channels + Redis (WebSocket bidding & live GPS streaming)
- **AI/ML Service:** FastAPI microservice (scikit-learn / XGBoost pricing & backhaul matching engine)
- **Async Workers:** Celery + Celery Beat
- **Database:** PostgreSQL 16 + PostGIS (relational + geospatial data)
- **Cache & Broker:** Redis 7
- **External APIs:** Razorpay (split payments & subscriptions), Exotel (SMS OTP & masked calling), Google Maps Platform

---

## 🚀 Local Development Setup

### Prerequisites

- Docker & Docker Compose (recommended)
- Python 3.12+ & `uv`
- Node.js 20+ & `pnpm`

### Using Docker (Quickest)

1. Clone the repo and copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Start the entire full-stack suite (Database, Redis, Backend, Celery, AI Service, Frontend):
   ```bash
   docker compose up --build
   ```

3. Access the services:
   - **Frontend PWA:** http://localhost:3000
   - **Backend API & Admin:** http://localhost:8000
   - **AI Microservice Docs:** http://localhost:8001/docs

---

## 📂 Project Structure

```
RoadLancer/
├── backend/            # Django 5 REST API & Channels WebSocket
├── frontend/           # Next.js 15 PWA client (Driver, Shipper, Fleet, Admin roles)
├── ai-service/         # FastAPI AI Price Floor & Backhaul Microservice
├── project-scope.md    # Product architecture & user roles spec
├── tech-stack.md       # Full engineering stack rationale
└── implementation-plan.md # ~240 atomic engineering tasks across 4 phases
```
