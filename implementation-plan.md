# RoadLancer — Implementation Plan

> **References:** [project-scope.md](./project-scope.md) · [tech-stack.md](./tech-stack.md)

---

## Phase 0 — Project Setup & Foundation

> **Goal:** Repository structure, tooling, Docker environment, CI/CD — everything needed before writing feature code.

### 0.1 Repository & Tooling

- [ ] Initialize Git repository + `.gitignore` (Python, Node, Docker, env files)
- [ ] Create top-level folder structure: `backend/`, `frontend/`, `ai-service/`
- [ ] Set up `README.md` with project overview and setup instructions
- [ ] Configure pre-commit hooks (ruff for Python, prettier + eslint for JS)

### 0.2 Backend Scaffolding (Django)

- [ ] Initialize Django project inside `backend/` using `django-admin startproject config .`
- [ ] Set up `uv` for dependency management with `pyproject.toml`
- [ ] Install core dependencies: Django, DRF, django-cors-headers, django-environ, psycopg2-binary, django-phonenumber-field
- [ ] Configure settings split: `base.py`, `development.py`, `production.py`
- [ ] Configure PostgreSQL as default database (with PostGIS engine)
- [ ] Configure Redis for caching (`django-redis`)
- [ ] Set up ASGI config for Django Channels (install `channels`, `channels-redis`)
- [ ] Set up Celery + Celery Beat with Redis broker
- [ ] Configure `django-storages` for S3-compatible file storage
- [ ] Set up CORS for frontend-backend communication
- [ ] Create the `core/` app (shared base models, permissions, utilities, middleware)
- [ ] Set up `pytest` + `pytest-django` for backend testing
- [ ] Create initial Dockerfile for backend

### 0.3 Frontend Scaffolding (Next.js)

- [ ] Initialize Next.js 15 project inside `frontend/` with App Router + TypeScript
- [ ] Set up `pnpm` as package manager
- [ ] Install and configure Tailwind CSS 4
- [ ] Install and configure shadcn/ui (init + base components: Button, Input, Card, Dialog, etc.)
- [ ] Set up `next-intl` for i18n with Hindi (`hi`) and English (`en`) locales
- [ ] Create translation files: `messages/en.json`, `messages/hi.json`
- [ ] Set up Zustand (create auth store, app store)
- [ ] Set up TanStack Query provider
- [ ] Set up React Hook Form + Zod for form handling
- [ ] Create API client utility (axios or fetch wrapper pointing to Django backend)
- [ ] Set up role-based routing structure: `(auth)/`, `driver/`, `shipper/`, `admin/`
- [ ] Create shared layout components (Sidebar, Header, MobileNav)
- [ ] Configure PWA: manifest.json, service worker, offline page, app icons
- [ ] Set up Vitest for frontend testing
- [ ] Create initial Dockerfile for frontend

### 0.4 Docker & Local Development

- [ ] Create `docker-compose.yml` with services: `backend`, `frontend`, `postgres`, `redis`, `celery-worker`, `celery-beat`
- [ ] Add volume mounts for hot-reloading in dev
- [ ] Create `.env.example` with all required environment variables
- [ ] Document local setup steps in README
- [ ] Verify entire stack runs with `docker compose up`

### 0.5 CI/CD Pipeline

- [ ] Create GitHub Actions workflow: lint → test → build on every PR
- [ ] Backend: ruff lint + pytest
- [ ] Frontend: eslint + prettier + vitest + next build
- [ ] Add Docker image build step (no deployment yet)

---

## Phase 1 — MVP (Core Marketplace Loop)

> **Goal:** A shipper can post a shipment, a driver can bid on it, lowest bid wins, payment happens, delivery is verified. This is the minimum viable marketplace.

---

### 1.1 User Accounts & Authentication

#### Backend

- [ ] Create `accounts` Django app
- [ ] Design User model (extends `AbstractBaseUser`):
  - Fields: phone, email (optional), role (driver/personal_shipper/business_shipper/enterprise_shipper/fleet_manager/admin), is_verified, is_active, language_preference
- [ ] Create role-specific profile models:
  - `DriverProfile`: license_number, vehicle_type, vehicle_capacity, vehicle_registration, aadhaar_number, pan_number, insurance_doc, verification_status, documents (FK to Document model)
  - `ShipperProfile`: shipper_type (personal/business/enterprise), gst_number, pan_number, company_name, business_address, verification_status
- [ ] Create `Document` model: user (FK), document_type (enum), file (S3), upload_date, verification_status, reviewed_by, review_notes
- [ ] Build OTP system:
  - Generate 6-digit OTP, store in Redis with 5-min TTL
  - API: `POST /api/auth/send-otp/` (phone → sends OTP via Exotel)
  - API: `POST /api/auth/verify-otp/` (phone + OTP → returns JWT tokens)
- [ ] JWT authentication (access + refresh tokens) using `djangorestframework-simplejwt`
- [ ] API endpoints:
  - `POST /api/auth/register/` (phone, role, basic profile)
  - `POST /api/auth/login/` (phone + OTP)
  - `GET /api/auth/me/` (current user profile)
  - `PATCH /api/auth/me/` (update profile)
  - `POST /api/auth/documents/` (upload verification documents)
  - `GET /api/auth/documents/` (list user's documents)
- [ ] Role-based permission classes: `IsDriver`, `IsShipper`, `IsAdmin`, `IsVerifiedDriver`
- [ ] Write unit tests for auth flow (register, OTP send/verify, login, JWT refresh)

#### Frontend

- [ ] **Login page** (`/(auth)/login`): phone input → OTP input → redirect to dashboard
- [ ] **Registration page** (`/(auth)/register`):
  - Step 1: Phone + OTP verification
  - Step 2: Role selection (I'm a Driver / I need to ship)
  - Step 3: Profile details (conditional on role)
  - Step 4: Document upload (for drivers)
- [ ] **Language selector** (Hindi/English toggle) — persisted in localStorage + user preference
- [ ] Auth Zustand store: user, tokens, login(), logout(), refreshToken()
- [ ] Protected route middleware: redirect to login if unauthenticated, redirect to correct dashboard based on role
- [ ] Phone number input component with Indian country code (+91) pre-filled
- [ ] OTP input component (6 digit, auto-focus, auto-submit)
- [ ] Write i18n translations for all auth screens (en + hi)

---

### 1.2 Shipment Management

#### Backend

- [ ] Create `shipments` Django app
- [ ] Design Shipment model:
  - Fields: shipper (FK), title, description, goods_category (enum: general/fragile/perishable/heavy_machinery), weight_kg, vehicle_type_required, pickup_city, pickup_address, pickup_pincode, dropoff_city, dropoff_address, dropoff_pincode, pickup_lat/lng, dropoff_lat/lng, distance_km, estimated_duration, urgency (urgent/standard/scheduled), scheduled_pickup_datetime, price_range_min, price_range_max, ai_price_floor, status (draft/published/bidding/won/pickup_confirmed/in_transit/delivered/payment_released/rated/cancelled/expired), bidding_window_minutes, bidding_start_time, bidding_end_time, winning_bid (FK), created_at, updated_at
- [ ] Integrate Google Maps Distance Matrix API:
  - Auto-calculate `distance_km` and `estimated_duration` from pickup/dropoff addresses
  - Geocode addresses to lat/lng on save
- [ ] Build AI price floor endpoint (Phase 1: rule-based, not ML):
  - Calculate based on distance × base_rate_per_km × weight_factor × goods_type_factor
  - Use seed data (government rate charts) for base rates
  - Endpoint: `POST /api/shipments/price-estimate/`
- [ ] API endpoints:
  - `POST /api/shipments/` (create shipment — shipper only)
  - `GET /api/shipments/` (list shipments — filterable by status, city, vehicle_type, goods_category)
  - `GET /api/shipments/{id}/` (detail — visibility rules based on role + bid status)
  - `PATCH /api/shipments/{id}/` (update — only draft status)
  - `DELETE /api/shipments/{id}/` (delete — only draft status)
  - `POST /api/shipments/{id}/publish/` (transition draft → published → bidding_open)
  - `POST /api/shipments/{id}/cancel/` (cancel with penalty logic if bid is already won)
- [ ] Pre-bid visibility filter: hide exact address + shipper name from drivers who haven't won
- [ ] Auto-set `bidding_end_time` based on urgency (5min / 30min / 24hr)
- [ ] Celery task: `check_bidding_expiry` — runs every 30 seconds, finds shipments where bidding window has ended, triggers winner selection
- [ ] Celery task: `no_bid_fallback` — if zero bids at expiry: send SMS to nearby drivers, suggest revised price range, extend window once, then expire
- [ ] Write unit tests for shipment CRUD, lifecycle transitions, visibility rules

#### Frontend

- [ ] **Post Shipment page** (`/shipper/shipments/new`):
  - Form: goods category, weight, vehicle type, pickup address (autocomplete), dropoff address (autocomplete)
  - Auto-calculated: distance, estimated time, AI price floor
  - Shipper sets price range (min ≥ AI floor, max ≥ min)
  - Urgency selector (Urgent / Standard / Scheduled)
  - If scheduled: date/time picker for pickup
  - Preview screen before publishing
- [ ] **Shipper Dashboard** (`/shipper/dashboard`):
  - Stats cards: active shipments, pending bids, completed, total spent
  - Shipment list with status badges and filters
  - Quick actions: view bids, track shipment, cancel
- [ ] **Shipment Detail page** (`/shipper/shipments/[id]`):
  - Full shipment info + status timeline
  - Live bid list (if bidding open) — shows bid amount, driver rating, vehicle info
  - Winner card (after bid won)
- [ ] **Browse Shipments page** (`/driver/shipments`):
  - Filterable list: by route (city), vehicle type, goods category, price range
  - Each card shows: route, distance, price range, time remaining, number of bids
  - Respects pre-bid visibility (no exact addresses)
- [ ] **Driver Dashboard** (`/driver/dashboard`):
  - Stats cards: active bids, won shipments, completed, total earned
  - Active shipments list with status
  - Recent bid history
- [ ] Address autocomplete component using Google Places API
- [ ] Shipment status badge component (color-coded per lifecycle state)
- [ ] Write i18n translations for all shipment screens

---

### 1.3 Bidding System

#### Backend

- [ ] Create `bidding` Django app
- [ ] Design Bid model:
  - Fields: shipment (FK), driver (FK), amount, status (pending/won/lost/withdrawn), placed_at, vehicle_info (snapshot of driver's vehicle at bid time)
- [ ] API endpoints:
  - `POST /api/shipments/{id}/bids/` (place bid — driver only, within bidding window, within price range)
  - `GET /api/shipments/{id}/bids/` (list bids — shipper sees all, driver sees own)
  - `DELETE /api/shipments/{id}/bids/{bid_id}/` (withdraw bid — only before window closes)
- [ ] Bid validation rules:
  - Driver must be verified
  - Bid amount must be within shipment's price_range_min–price_range_max
  - Bid must be placed before bidding_end_time
  - Driver can't bid on same shipment twice
  - Check driver's active shipment capacity (vehicle-based)
- [ ] Winner selection logic (triggered by `check_bidding_expiry` Celery task):
  - Select lowest bid
  - If tie: pick the bid placed first
  - Update winning bid status → `won`, all others → `lost`
  - Update shipment status → `won`
  - Set shipment.winning_bid = winning bid
- [ ] Post-win notifications (trigger via Celery):
  - SMS to winner: "You won the bid! Pickup details: [address], [time]"
  - SMS to shipper: "A driver has been assigned to your shipment"
  - In-app notifications to all bidders (won/lost)
- [ ] Django Channels WebSocket consumer for real-time bidding:
  - `BiddingConsumer`: handles group `shipment_{id}_bids`
  - Broadcasts new bids to all connected clients in real-time
  - Broadcasts bid countdown timer sync
  - Broadcasts winner announcement
- [ ] Write unit tests for bid placement, validation, winner selection, edge cases

#### Frontend

- [ ] **Bid Placement UI** (on shipment detail for drivers):
  - Price range slider or input within allowed range
  - "Place Bid" button with confirmation dialog
  - Current lowest bid indicator
  - Number of total bids counter
- [ ] **Live Bidding View** (for shippers watching bids come in):
  - Real-time bid list (via WebSocket) — shows new bids appearing live
  - Countdown timer to bidding window close
  - Bid statistics: lowest, average, number of bids
- [ ] **Bid Countdown Timer component**:
  - Shows remaining time (mm:ss for urgent, hh:mm:ss for standard/scheduled)
  - Synced via WebSocket to prevent client clock drift
  - Visual urgency (green → yellow → red as time runs out)
- [ ] WebSocket hook: `useWebSocket(shipmentId)` — connects to Django Channels, handles reconnect
- [ ] **My Bids page** (`/driver/bids`):
  - Active bids (pending)
  - Won bids (with pickup details)
  - Lost bids (history)
- [ ] Bid won celebration animation/toast
- [ ] Write i18n translations for bidding UI

---

### 1.4 Delivery Verification

#### Backend

- [ ] Add delivery verification fields to Shipment model:
  - `pickup_otp` (auto-generated 4-digit), `delivery_otp` (auto-generated 4-digit)
  - `pickup_photo` (S3), `delivery_photo` (S3)
  - `pickup_confirmed_at`, `delivered_at`
- [ ] API endpoints:
  - `POST /api/shipments/{id}/generate-pickup-otp/` (shipper generates OTP, sent to shipper via SMS)
  - `POST /api/shipments/{id}/confirm-pickup/` (driver submits OTP + photo → status: `pickup_confirmed`)
  - `POST /api/shipments/{id}/generate-delivery-otp/` (shipper sends OTP to recipient)
  - `POST /api/shipments/{id}/confirm-delivery/` (driver submits OTP + photo → status: `delivered`)
- [ ] Photo upload: compress on backend (Pillow), store on S3
- [ ] Status transitions: `won` → `pickup_confirmed` → `in_transit` → `delivered`
- [ ] Write unit tests for OTP generation, verification, photo upload, status transitions

#### Frontend

- [ ] **Pickup Confirmation screen** (driver):
  - Enter OTP from shipper
  - Camera capture for photo proof of goods condition
  - "Confirm Pickup" button
- [ ] **Delivery Confirmation screen** (driver):
  - Enter OTP from recipient
  - Camera capture for photo proof of delivered goods
  - "Confirm Delivery" button
- [ ] **OTP Display screen** (shipper):
  - Shows the generated OTP to share with driver (at pickup) or recipient (at delivery)
- [ ] Camera capture component: uses `navigator.mediaDevices.getUserMedia` for PWA camera access
- [ ] Write i18n translations for verification screens

---

### 1.5 Payment Integration

#### Backend

- [ ] Create `payments` Django app
- [ ] Design Payment model:
  - Fields: shipment (FK), payer (FK to shipper), payee (FK to driver), amount, platform_fee (2%), driver_payout, status (pending/processing/held/released/failed), razorpay_order_id, razorpay_payment_id, payment_date, hold_until (delivery_date + 3-5 days), released_at
- [ ] Razorpay integration:
  - `POST /api/payments/{shipment_id}/create-order/` — creates Razorpay order after delivery confirmation
  - `POST /api/payments/webhook/` — Razorpay webhook handler (verify signature, update payment status)
  - `POST /api/payments/{shipment_id}/verify/` — verify payment on frontend callback
- [ ] Payment flow:
  1. Shipment delivered → payment status: `pending`
  2. Shipper pays via Razorpay → status: `processing` → `held`
  3. Hold for 3-5 days → Celery Beat task: `release_held_payments` → status: `released`
  4. Razorpay Route payout to driver bank account (minus 2%)
- [ ] Celery Beat task: `release_held_payments` — runs daily, finds payments where `hold_until <= now()`, triggers Razorpay payout
- [ ] Celery Beat task: `payment_reminder` — if shipper hasn't paid within 48 hours of delivery, send SMS reminder
- [ ] Driver Wallet model (for tracking earnings):
  - Fields: driver (FK), total_earned, available_balance, pending_balance
  - Updated on each payment release
- [ ] API endpoints:
  - `GET /api/payments/history/` (user's payment history)
  - `GET /api/payments/wallet/` (driver's wallet balance)
- [ ] Write unit tests for payment flow, webhook handling, payout calculation

#### Frontend

- [ ] **Payment page** (shipper — after delivery):
  - Shipment summary
  - Amount breakdown: bid amount + 2% platform fee = total
  - Razorpay checkout button (opens Razorpay modal)
  - Payment success/failure screen
- [ ] **Earnings page** (`/driver/earnings`):
  - Wallet balance card (available, pending, total earned)
  - Payment history list with status badges
  - Payout details (bank account info)
- [ ] Razorpay checkout integration (Razorpay JS SDK in Next.js)
- [ ] Write i18n translations for payment screens

---

### 1.6 Notification System

#### Backend

- [ ] Create `notifications` Django app
- [ ] Design Notification model:
  - Fields: user (FK), type (enum: bid_placed, bid_won, bid_lost, shipment_update, payment_received, etc.), title, message, data (JSON), is_read, created_at
- [ ] Notification service (centralized):
  - `send_sms(phone, message)` — via Exotel API
  - `send_push(user, title, body, data)` — via FCM
  - `send_in_app(user, type, title, message, data)` — save to DB + broadcast via WebSocket
  - `send_notification(user, type, channels=[sms, push, in_app])` — dispatcher that sends via requested channels
- [ ] Exotel SMS integration:
  - OTP sending
  - Bid won/lost alerts
  - Payment reminders
  - Delivery confirmations
- [ ] FCM push notification integration:
  - Store user's FCM token on frontend registration
  - Send push via `firebase-admin` Python SDK
- [ ] WebSocket consumer for in-app notifications:
  - `NotificationConsumer`: personal channel per user
  - Real-time delivery of in-app notifications
- [ ] API endpoints:
  - `GET /api/notifications/` (list user's notifications, paginated)
  - `PATCH /api/notifications/{id}/read/` (mark as read)
  - `POST /api/notifications/mark-all-read/` (mark all as read)
  - `POST /api/notifications/fcm-token/` (register device FCM token)
- [ ] Write unit tests for notification dispatch, SMS sending, FCM integration

#### Frontend

- [ ] **Notification bell** (in header): unread count badge, dropdown with recent notifications
- [ ] **Notifications page** (`/notifications`): full list, mark as read, filter by type
- [ ] FCM service worker registration + push notification handling
- [ ] Push notification permission request flow (prompt on first login, don't block)
- [ ] Toast/snackbar for real-time in-app notifications
- [ ] Write i18n translations for all notification messages

---

### 1.7 MVP Polish & Testing

- [ ] **Interactive onboarding walkthrough** for drivers (react-joyride):
  - Step 1: "Browse available shipments here"
  - Step 2: "Tap to view details and place a bid"
  - Step 3: "Track your active shipments"
  - Step 4: "View your earnings"
- [ ] **Landing page** (`/`): hero section, how it works, driver CTA, shipper CTA
- [ ] **Responsive design** pass: ensure all screens work on mobile (320px+) and desktop
- [ ] **Loading states**: skeleton screens for lists, spinner for actions
- [ ] **Error handling**: error boundaries, API error toasts, retry logic
- [ ] **Empty states**: "No shipments yet", "No bids received", etc. — with illustrations
- [ ] End-to-end testing: full flow from shipment posting → bidding → winner → pickup → delivery → payment
- [ ] Security review: input validation, SQL injection prevention (Django ORM handles), XSS (React handles), CSRF, rate limiting on OTP endpoint
- [ ] Performance: lazy loading routes, image optimization (next/image), API pagination
- [ ] Accessibility pass: ARIA labels, keyboard navigation, color contrast (especially for low-literacy driver UI)

---

## Phase 2 — Core Experience

> **Goal:** GPS tracking, ratings, AI pricing, chat, admin panel, subscriptions — making the platform production-ready and trustworthy.

---

### 2.1 GPS Tracking

#### Backend

- [ ] Create `tracking` Django app
- [ ] Design LocationPoint model: shipment (FK), driver (FK), latitude, longitude, speed, timestamp
- [ ] WebSocket consumer: `TrackingConsumer`
  - Driver sends location updates every 15-30 seconds
  - Shipper subscribes to shipment's location channel
  - Store each point in DB + broadcast to shipper
- [ ] SMS-based fallback: Celery task that pings driver via SMS if no WebSocket update for 5+ minutes, driver replies with location (parsed)
- [ ] API endpoints:
  - `GET /api/shipments/{id}/tracking/` (location history for a shipment)
  - `GET /api/shipments/{id}/tracking/live/` (latest location)

#### Frontend

- [ ] **Live Tracking Map** (shipper view): Google Maps with driver marker updating in real-time via WebSocket
- [ ] **Driver tracking widget**: "Your location is being shared" indicator with toggle
- [ ] Route polyline overlay on map (pickup → current → dropoff)
- [ ] ETA calculation display based on remaining distance

---

### 2.2 Rating System

#### Backend

- [ ] Create `ratings` Django app
- [ ] Design Rating model:
  - Fields: shipment (FK), rater (FK), ratee (FK), overall_score (1-5), dimensions (JSON: {punctuality, goods_condition, communication, professionalism}), review_text, created_at
- [ ] Badge model: user (FK), badge_type (enum: 100_deliveries, zero_damage, premium_shipper, etc.), earned_at
- [ ] Rating rules:
  - Both parties rate each other after delivery
  - Rating window: 7 days after delivery
  - Can't modify rating after submission
- [ ] Aggregate rating calculation on User profile: avg_rating, total_ratings, dimension_averages
- [ ] Minimum threshold enforcement: if avg_rating < 3.5 after 10+ ratings → flag for admin review
- [ ] Badge auto-award: Celery task checks milestones after each completed shipment
- [ ] API endpoints:
  - `POST /api/shipments/{id}/rate/` (submit rating)
  - `GET /api/users/{id}/ratings/` (view user's received ratings)
  - `GET /api/users/{id}/badges/` (view user's badges)

#### Frontend

- [ ] **Rate Shipment modal** (post-delivery prompt): star rating per dimension + optional text review
- [ ] **User Profile page**: overall rating, dimension breakdown chart, badge gallery, review list
- [ ] Badge display component (icons + tooltips)
- [ ] Rating prompt notification after delivery

---

### 2.3 AI Pricing Engine

#### Backend (FastAPI microservice)

- [ ] Set up FastAPI project inside `ai-service/`
- [ ] Create seed data pipeline:
  - Collect government transport rate charts
  - Build fuel price dataset (per-state diesel prices)
  - Create distance matrix for top 100 Indian routes
  - Manual baseline pricing for 50-100 common corridors
- [ ] Build pricing model (v1: scikit-learn regression):
  - Features: distance_km, weight_kg, goods_category, vehicle_type, pickup_state, dropoff_state, day_of_week, month
  - Target: fair_price (from seed data initially, then from real transactions)
  - Train/test split, cross-validation, performance metrics
- [ ] API endpoints:
  - `POST /api/ai/price-estimate` → returns {estimated_min, estimated_max, floor_price, confidence}
  - `POST /api/ai/retrain` → triggers model retraining on latest data
- [ ] Django integration: call FastAPI from Django when shipment is created (to get AI floor)
- [ ] Celery Beat task: retrain model weekly with new transaction data
- [ ] Create Dockerfile for ai-service
- [ ] Add ai-service to docker-compose.yml

---

### 2.4 In-App Chat & Masked Calls

#### Backend

- [ ] Create `chat` Django app
- [ ] Design Message model: conversation (FK), sender (FK), content, message_type (text/image/system), sent_at, read_at
- [ ] Design Conversation model: shipment (FK), participants (M2M), created_at
- [ ] WebSocket consumer: `ChatConsumer` for real-time messaging
- [ ] API endpoints:
  - `GET /api/shipments/{id}/chat/` (get/create conversation)
  - `GET /api/chat/{conversation_id}/messages/` (paginated message history)
  - `POST /api/chat/{conversation_id}/messages/` (send message — fallback to REST if WebSocket fails)
- [ ] Exotel masked calling integration:
  - `POST /api/shipments/{id}/call/` → generates Exotel ExoPhone masked call between driver and shipper
  - Call logs stored for dispute resolution

#### Frontend

- [ ] **Chat interface** (within shipment detail): message list, input box, real-time via WebSocket
- [ ] **Call button**: initiates masked call via Exotel, shows "Calling..." status
- [ ] Unread message indicator on shipment cards

---

### 2.5 Admin Panel

#### Backend

- [ ] Create `admin_panel` Django app (extends Django admin + custom API endpoints)
- [ ] API endpoints for admin:
  - `GET /api/admin/users/` (list + filter + search all users)
  - `PATCH /api/admin/users/{id}/` (approve, suspend, ban)
  - `GET /api/admin/documents/pending/` (document verification queue)
  - `PATCH /api/admin/documents/{id}/verify/` (approve/reject document with notes)
  - `GET /api/admin/disputes/` (list disputes)
  - `PATCH /api/admin/disputes/{id}/resolve/` (resolve with decision)
  - `GET /api/admin/analytics/` (dashboard stats: users, shipments, revenue, bids)
  - `GET /api/admin/shipments/active/` (live shipments for map view)
  - `POST /api/admin/announcements/` (broadcast announcement to all users)
  - `PATCH /api/admin/price-floors/` (override AI price floors for specific routes)

#### Frontend

- [ ] **Admin Dashboard** (`/admin/dashboard`): stats cards (users, revenue, shipments, active bids)
- [ ] **User Management** (`/admin/users`): data table with search, filter by role/status, approve/suspend/ban actions
- [ ] **Document Verification** (`/admin/documents`): queue view, document preview (image viewer), approve/reject with notes
- [ ] **Dispute Resolution** (`/admin/disputes`): dispute list, evidence viewer (photos, GPS, chat logs), resolution form
- [ ] **Financial Dashboard** (`/admin/finance`): revenue chart (Recharts), pending payouts, commission breakdown
- [ ] **Live Shipment Map** (`/admin/tracking`): Google Maps with all active shipment locations
- [ ] **Announcements** (`/admin/announcements`): create + broadcast notifications

---

### 2.6 Shipper Subscriptions

#### Backend

- [ ] Add subscription logic to `payments` app:
  - Subscription model: shipper (FK), plan (free/business/enterprise), status (active/expired/cancelled), razorpay_subscription_id, current_period_start, current_period_end, shipments_used_this_month
- [ ] Razorpay Subscriptions integration:
  - Create subscription plan on Razorpay (₹1,000/month for Business)
  - Handle subscription creation, renewal, cancellation via webhook
- [ ] Shipment posting limit enforcement:
  - Free: unlimited (Personal shippers — commission only)
  - Business: 10 free/month → then ₹1,000/month for 50 → ₹100/additional
  - Enterprise: custom limits
- [ ] API endpoints:
  - `GET /api/subscriptions/current/` (current plan + usage)
  - `POST /api/subscriptions/upgrade/` (start Razorpay subscription)
  - `POST /api/subscriptions/cancel/` (cancel subscription)

#### Frontend

- [ ] **Subscription page** (`/shipper/subscription`): current plan, usage meter, upgrade CTA
- [ ] **Plan selection UI**: compare plans, select, Razorpay checkout for Business tier
- [ ] Usage warning when approaching limit

---

### 2.7 Phase 2 Polish

- [ ] Dispute creation flow for users (report an issue → automated tier 1 → escalation)
- [ ] Cancellation flow with grace period + financial penalty + reputation hit
- [ ] Shipper cancellation flow with driver compensation
- [ ] "No bids" fallback chain (notify nearby, suggest price revision, extend, expire)
- [ ] Performance optimization: DB query optimization (select_related, prefetch_related), Redis caching for hot data
- [ ] Load testing with simulated concurrent bids (Locust or k6)
- [ ] Security audit: JWT expiry, rate limiting, input sanitization, webhook signature verification

---

## Phase 3 — Growth & Differentiation

> **Goal:** Fleet management, AI-powered backhaul matching, insurance, advanced analytics — features that create competitive moats.

---

### 3.1 Fleet Manager Dashboard

#### Backend

- [ ] Create `fleet` Django app
- [ ] Design Fleet model: owner (FK), name, vehicles (reverse FK)
- [ ] Design FleetVehicle model: fleet (FK), assigned_driver (FK, nullable), vehicle_type, registration_number, capacity, status (available/assigned/maintenance)
- [ ] API endpoints:
  - `POST /api/fleet/vehicles/` (add vehicle)
  - `GET /api/fleet/vehicles/` (list fleet vehicles)
  - `POST /api/fleet/vehicles/{id}/assign-driver/` (assign driver to vehicle)
  - `GET /api/fleet/dashboard/` (aggregate: total vehicles, active shipments, total earnings)

#### Frontend

- [ ] **Fleet Dashboard** (`/fleet/dashboard`): vehicle count, active shipments, earnings overview
- [ ] **Vehicle Management** (`/fleet/vehicles`): add/edit vehicles, assign drivers, status tracking
- [ ] **Fleet Earnings** (`/fleet/earnings`): per-vehicle and per-driver earnings breakdown
- [ ] **Fleet Bidding**: bid on shipments and assign to specific vehicle/driver

---

### 3.2 AI Backhaul Matching

#### Backend (FastAPI)

- [ ] Build backhaul matching algorithm:
  - Input: driver's current drop-off location, vehicle type, availability window
  - Query: find published/bidding shipments within X km of drop-off location (PostGIS query)
  - Score: by distance from drop-off, price, route alignment with driver's home base
  - Output: ranked list of recommended return-load shipments
- [ ] `POST /api/ai/backhaul-suggest` endpoint
- [ ] Celery task: after shipment delivery confirmed → auto-generate backhaul suggestions → notify driver via push + SMS
- [ ] Track backhaul conversion rate (suggested → bid → won) for model improvement

#### Frontend

- [ ] **Backhaul Suggestions card** (on driver dashboard after delivery): "Shipments near you" carousel
- [ ] **Backhaul notification**: push notification with top 3 suggestions
- [ ] Quick-bid button directly from suggestion card

---

### 3.3 Insurance Integration

#### Backend

- [ ] Add insurance fields to Shipment model: is_insured, insurance_provider, insurance_policy_id, insured_value, insurance_premium
- [ ] Insurance quote API (partner API integration or rule-based calculator):
  - Input: goods_category, weight, value, distance
  - Output: premium amount
- [ ] API endpoints:
  - `POST /api/shipments/{id}/insurance-quote/` (get quote)
  - `POST /api/shipments/{id}/purchase-insurance/` (purchase via Razorpay add-on payment)

#### Frontend

- [ ] **Insurance option** on shipment posting: "Protect your goods" toggle with quote display
- [ ] Insurance badge on shipment cards
- [ ] Insurance claim link in dispute flow

---

### 3.4 Advanced Analytics

#### Backend

- [ ] Analytics aggregation Celery tasks (daily/weekly):
  - Route popularity heatmap data
  - Average pricing trends per route
  - Bid pattern analysis (time-to-bid, bid distribution)
  - User growth metrics
  - Revenue breakdown (commissions, subscriptions, insurance)
- [ ] API endpoints:
  - `GET /api/analytics/routes/` (popular routes, avg prices)
  - `GET /api/analytics/pricing-trends/` (price history per route)
  - `GET /api/analytics/platform/` (admin: overall platform stats)

#### Frontend

- [ ] **Shipper Analytics** (`/shipper/analytics`): spending trends, price history per route, savings vs market rate
- [ ] **Driver Analytics** (`/driver/analytics`): earnings trends, best routes, completion rate
- [ ] **Admin Analytics** (`/admin/analytics`): full platform dashboard with charts (users, revenue, shipments, route heatmap)

---

### 3.5 Enterprise Features

- [ ] Enterprise shipper onboarding flow (custom contracts, dedicated account manager assignment)
- [ ] Bulk shipment posting (CSV upload → create multiple shipments at once)
- [ ] API access for enterprise shippers (API key management, rate limiting, webhook callbacks)
- [ ] Custom pricing tiers (negotiated commission rates)
- [ ] Monthly invoice generation (PDF) for enterprise accounts

---

### 3.6 E-Way Bill Integration

- [ ] Integrate with GST e-way bill portal API
- [ ] Auto-populate e-way bill fields from shipment data
- [ ] `POST /api/shipments/{id}/generate-eway-bill/` endpoint
- [ ] E-way bill display for driver (in shipment detail during transit)
- [ ] E-way bill expiry tracking and alerts

---

### 3.7 Additional Languages

- [ ] Add translation files for: Tamil, Telugu, Marathi, Gujarati, Bengali, Kannada
- [ ] Language auto-detection based on user's phone locale
- [ ] UI translation review by native speakers
- [ ] Right-to-left (RTL) support evaluation (for Urdu if needed)

---

### 3.8 Gamification & Engagement

- [ ] Advanced badge system: streak badges (5 consecutive on-time deliveries), milestone badges (₹1L earned), category badges (fragile goods specialist)
- [ ] Driver leaderboard (top earners per route corridor — monthly)
- [ ] Referral system: driver invites driver → both get bonus on first completed shipment
- [ ] Loyalty rewards: reduced commission after 100+ completed shipments

---

## Deployment Milestones

| Milestone | Phase | What's Live |
|-----------|-------|-------------|
| **Internal Alpha** | Phase 0 + 1.1–1.3 | Auth + shipment posting + bidding (no payments, no verification) |
| **Closed Beta** | Phase 1 complete | Full MVP: post → bid → win → pickup → deliver → pay. Test with 20-50 users on one corridor. |
| **Public Launch** | Phase 2.1–2.5 | GPS tracking, ratings, AI pricing, chat, admin panel. Open to all users on launch corridor. |
| **Growth** | Phase 3 | Fleet manager, backhaul, insurance, analytics. Expand to additional corridors. |

---

## Task Estimation Summary

| Phase | Sections | Estimated Tasks |
|-------|----------|-----------------|
| **Phase 0** — Setup | 5 sections | ~30 tasks |
| **Phase 1** — MVP | 7 sections | ~90 tasks |
| **Phase 2** — Core Experience | 7 sections | ~70 tasks |
| **Phase 3** — Growth | 8 sections | ~50 tasks |
| **Total** | | **~240 tasks** |

> [!NOTE]
> Each task above is intentionally small and atomic — most can be completed in 1-4 hours. Track progress by checking off tasks as you go.
