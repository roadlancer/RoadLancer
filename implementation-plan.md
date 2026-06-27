# RoadLancer — Implementation Plan (College Project)

> **References:** [project-scope.md](./project-scope.md) · [tech-stack.md](./tech-stack.md)

---

## Phase 0 — Project Setup

> **Goal:** Get the development environment running locally.

### 0.1 Prerequisites

- [ ] Install PHP 8.2+ with extensions (`mbstring`, `xml`, `curl`, `pgsql`, `zip`)
- [ ] Install Composer 2.x
- [ ] Install Node.js 20+ and npm
- [ ] Install PostgreSQL 16 (local or Docker)
- [ ] Install Python 3.11+ and `uv` (for AI microservice)
- [ ] Create PostgreSQL database: `roadlancer` (user: `postgres`, password: `postgres`)

### 0.2 Laravel Setup

- [ ] Scaffold Laravel project: `composer create-project laravel/laravel .`
- [ ] Copy `.env.example` to `.env` and configure database credentials
- [ ] Generate app key: `php artisan key:generate`
- [ ] Run migrations: `php artisan migrate`
- [ ] Verify: `php artisan serve` → visit http://localhost:8000

### 0.3 Vue.js + Tailwind Setup

- [ ] Install Vue.js: `npm install vue @vitejs/plugin-vue`
- [ ] Install Tailwind CSS: `npm install -D tailwindcss @tailwindcss/vite`
- [ ] Configure `vite.config.js` with Vue and Tailwind plugins
- [ ] Create Vue entry point: `resources/js/app.js`
- [ ] Create base Blade layout with `@vite` directive
- [ ] Verify: `npm run dev` → Vite starts with hot reload

### 0.4 AI Microservice

- [x] FastAPI microservice with `/price-estimate` endpoint
- [x] Start with: `cd ai-service && uv run uvicorn app.main:app --port 8001`
- [x] Verify: visit http://localhost:8001/docs

---

## Phase 1 — Authentication & User Management

> **Goal:** Users can register, login, and access role-specific dashboards.

### 1.1 Database Migrations

- [ ] Create `users` migration: name, email, password, phone, role (enum: driver/shipper/admin), is_verified, timestamps
- [ ] Create `sessions` migration: `php artisan session:table`
- [ ] Run migrations

### 1.2 User Model & Auth

- [ ] Update User model with `role` enum casting, `phone` and `is_verified` fields
- [ ] Create `RegisterController` — register with name, email, password, phone, role
- [ ] Create `LoginController` — login with email + password
- [ ] Create `LogoutController` — destroy session
- [ ] Create role-based middleware: `EnsureRole` (driver, shipper, admin)

### 1.3 Auth Views

- [ ] Create Blade layout (`resources/views/layouts/app.blade.php`)
- [ ] Create login page (`resources/views/auth/login.blade.php`)
- [ ] Create register page (`resources/views/auth/register.blade.php`)
- [ ] Create navigation bar with role-based menu items
- [ ] Redirect after login: drivers → driver dashboard, shippers → shipper dashboard

### 1.4 Dashboards (Skeleton)

- [ ] Create driver dashboard page (placeholder)
- [ ] Create shipper dashboard page (placeholder)
- [ ] Create admin dashboard page (placeholder)
- [ ] Seed an admin user: `admin@roadlancer.in` / `password`

---

## Phase 2 — Shipments & AI Pricing

> **Goal:** Shippers can create shipments with AI-calculated pricing.

### 2.1 Shipment Model & Migration

- [ ] Create `shipments` migration (see project-scope.md for schema)
- [ ] Create Shipment Eloquent model with relationships (belongsTo shipper, hasMany bids)
- [ ] Create ShipmentController with CRUD methods

### 2.2 AI Price Integration

- [ ] Create `AiPricingService` class — HTTP client that calls FastAPI `/price-estimate`
- [ ] On shipment creation: auto-call AI service, populate `ai_floor_price`, `ai_estimated_min`, `ai_estimated_max`
- [ ] Display AI price range on shipment creation form

### 2.3 Shipment Views

- [ ] Create shipment creation form (Blade + Vue component for dynamic pricing display)
- [ ] Create shipment listing page (filterable by status, goods category)
- [ ] Create shipment detail page (shows all info + bid list)
- [ ] Shipper dashboard: "My Shipments" list with status badges

### 2.4 Shipment Status Updates

- [ ] Create status update API endpoint
- [ ] Driver can mark: `in_transit` → `delivered`
- [ ] Shipper can mark: `delivered` → `completed`
- [ ] Status badge colors on listing page

---

## Phase 3 — Bidding System

> **Goal:** Drivers can bid on shipments, shippers can accept bids.

### 3.1 Bid Model & Migration

- [ ] Create `bids` migration (see project-scope.md for schema)
- [ ] Create Bid Eloquent model with relationships
- [ ] Validate: bid amount >= AI floor price

### 3.2 Bidding API

- [ ] `POST /api/shipments/{id}/bids` — place a bid (driver only)
- [ ] `GET /api/shipments/{id}/bids` — list all bids for a shipment
- [ ] `PUT /api/bids/{id}/accept` — accept a bid (shipper only, auto-rejects others)
- [ ] On bid acceptance: update shipment status to `assigned`, set `assigned_driver_id`

### 3.3 Bidding UI

- [ ] Vue component: BiddingPanel (shows current bids, place new bid form)
- [ ] Real-time updates via polling (refresh bid list every 5 seconds using `setInterval`)
- [ ] Driver dashboard: "My Bids" list with status
- [ ] Countdown timer display (visual only, based on `bidding_ends_at`)

---

## Phase 4 — Verification & Completion

> **Goal:** OTP-based pickup/delivery verification.

### 4.1 Verification Model & Migration

- [ ] Create `verifications` migration (see project-scope.md for schema)
- [ ] Create Verification model

### 4.2 OTP Flow

- [ ] Generate random 4-digit OTP on shipment assignment (for pickup)
- [ ] Display OTP to shipper on their dashboard
- [ ] Driver enters OTP to confirm pickup → status changes to `in_transit`
- [ ] Generate new OTP for delivery
- [ ] Shipper enters delivery OTP → status changes to `delivered`
- [ ] *(Mock OTP — no real SMS integration, just displayed on screen)*

### 4.3 Verification UI

- [ ] Vue component: OTP input (4 digit boxes)
- [ ] Success/error toast notifications

---

## Phase 5 — Admin Panel & Analytics

> **Goal:** Admin can manage the platform and view basic analytics.

### 5.1 Admin Features

- [ ] User management: list all users, view details, toggle verification status
- [ ] Shipment management: list all shipments, view details, filter by status
- [ ] Basic moderation: ability to cancel shipments, ban users

### 5.2 Analytics Dashboard

- [ ] Total users count (drivers vs shippers)
- [ ] Total shipments by status (pie chart)
- [ ] Shipments over time (line chart)
- [ ] Average bid amounts (bar chart)
- [ ] Vue component with Chart.js visualizations

---

## Phase 6 — Polish & Presentation

> **Goal:** Make it demo-ready for college submission.

### 6.1 UI Polish

- [ ] Consistent Tailwind styling across all pages
- [ ] Mobile responsive layouts
- [ ] Loading spinners and error states
- [ ] Empty state illustrations ("No shipments yet")
- [ ] Toast notifications for actions (bid placed, shipment created, etc.)

### 6.2 Seed Data

- [ ] Create database seeder with sample users (3 drivers, 2 shippers, 1 admin)
- [ ] Create sample shipments across different statuses
- [ ] Create sample bids on active shipments
- [ ] Run with: `php artisan db:seed`

### 6.3 Documentation

- [ ] Update README.md with final setup instructions
- [ ] Add screenshots to README
- [ ] Prepare demo script (walkthrough of all features)
- [ ] Create project report / presentation slides
