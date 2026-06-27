# RoadLancer 🚛

**AI-Powered Transportation Management & Direct Trucking Marketplace for India**

RoadLancer eliminates 40-60% middleman margins in India's trucking industry by connecting drivers directly with shippers (personal, business, enterprise) through AI-enforced price floors, transparent bidding windows, and double verification (Photo + OTP).

---

## 🏗️ Tech Stack

- **Backend:** Laravel 12 (PHP 8.2+, Eloquent ORM, Blade templates, Laravel Queue)
- **Frontend:** Vue.js 3 (embedded in Blade via Vite, Single File Components)
- **Authentication:** Laravel native session auth (email/password, bcrypt, database sessions)
- **AI/ML Service:** FastAPI microservice (scikit-learn / XGBoost pricing & backhaul matching engine)
- **Real-Time:** Laravel Reverb / Pusher (WebSocket bidding & live GPS streaming)
- **Database:** PostgreSQL 16 + PostGIS (relational + geospatial data)
- **Cache & Broker:** Redis 7 (caching, queue broker, session driver)
- **External APIs:** Razorpay (split payments & subscriptions), Exotel (SMS OTP & masked calling), Google Maps Platform

---

## 🚀 Local Development Setup

### Prerequisites

- PHP 8.2+ with extensions: `mbstring`, `xml`, `curl`, `pgsql`, `zip`
- Composer 2.x
- Node.js 20+ & `npm`
- PostgreSQL 16 (or Docker)
- Redis 7 (or Docker)

### Quick Start

1. Clone the repo and copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   composer install
   npm install
   ```

3. Generate app key and run migrations:
   ```bash
   php artisan key:generate
   php artisan migrate
   ```

4. Start development servers:
   ```bash
   # Terminal 1: Laravel backend
   php artisan serve

   # Terminal 2: Vite dev server (Vue hot reload)
   npm run dev

   # Terminal 3: Queue worker
   php artisan queue:work redis

   # Terminal 4: AI microservice
   cd ai-service && uv run uvicorn app.main:app --port 8001
   ```

5. Access the services:
   - **Application:** http://localhost:8000
   - **AI Microservice Docs:** http://localhost:8001/docs

### Using Docker

```bash
docker compose up --build
```

---

## 📂 Project Structure

```
RoadLancer/
├── app/                    # Laravel application (Models, Controllers, Middleware)
│   ├── Http/Controllers/   # Request handlers
│   ├── Models/             # Eloquent models
│   └── Jobs/               # Queue jobs (bid expiry, payments, OTP)
├── resources/
│   ├── views/              # Blade templates
│   ├── js/                 # Vue.js 3 components & app entry
│   └── css/                # Stylesheets
├── routes/
│   ├── web.php             # Blade page routes
│   └── api.php             # REST API endpoints
├── database/
│   └── migrations/         # Database migrations
├── ai-service/             # FastAPI AI Price Floor & Backhaul Microservice
├── project-scope.md        # Product architecture & user roles spec
├── tech-stack.md           # Full engineering stack rationale
└── implementation-plan.md  # Engineering tasks across phases
```
