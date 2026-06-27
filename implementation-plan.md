# RoadLancer — Implementation Plan

> **References:** [project-scope.md](./project-scope.md) · [tech-stack.md](./tech-stack.md)

---

## Phase 0 — Project Setup & Foundation

> **Goal:** Repository structure, tooling, Docker environment — everything needed before writing feature code.

### 0.1 Repository & Tooling

- [ ] Clean project root (remove old Django/Next.js artifacts)
- [ ] Update `.gitignore` for PHP/Laravel/Node
- [ ] Update `README.md` with Laravel setup instructions
- [ ] Configure pre-commit hooks (Laravel Pint for PHP, Prettier + ESLint for JS)

### 0.2 Laravel Scaffolding

- [ ] Scaffold Laravel 12 project using `composer create-project laravel/laravel`
- [ ] Configure `.env` with PostgreSQL credentials (`postgres:postgres@localhost:5432/roadlancer`)
- [ ] Configure `config/database.php` for PostgreSQL connection
- [ ] Configure `config/queue.php` with Redis driver
- [ ] Configure `config/cache.php` with Redis driver
- [ ] Configure `config/session.php` with database driver
- [ ] Install and configure Laravel CORS (`config/cors.php`)
- [ ] Create session migration (`php artisan session:table`)
- [ ] Run initial migrations (`php artisan migrate`)
- [ ] Create Dockerfile for Laravel (PHP-FPM + Nginx or `artisan serve`)

### 0.3 Vue.js Integration

- [ ] Install Vue.js 3 + `@vitejs/plugin-vue` via npm
- [ ] Configure `vite.config.js` with Vue plugin
- [ ] Create Vue app entry point (`resources/js/app.js`)
- [ ] Install Tailwind CSS 4 and configure
- [ ] Create base Blade layout (`resources/views/layouts/app.blade.php`) with `@vite` directive
- [ ] Create welcome/landing Blade view with embedded Vue component
- [ ] Install Axios for API calls
- [ ] Install Pinia for state management

### 0.4 AI Microservice (Preserved)

- [x] FastAPI microservice with `/price-estimate` and `/backhaul-suggest` endpoints
- [x] Health check verified on `http://localhost:8001/`

### 0.5 Docker Compose

- [ ] Update `docker-compose.yml` for Laravel services
  - [ ] `app` service: Laravel PHP-FPM
  - [ ] `nginx` service: Reverse proxy for Laravel
  - [ ] `queue-worker` service: `php artisan queue:work redis`
  - [ ] `scheduler` service: `php artisan schedule:run` (cron)
  - [ ] Keep `postgres`, `redis`, `ai-service` services
  - [ ] Remove old Django `backend`, `celery-worker`, `celery-beat`, `frontend` services

---

## Phase 1 — MVP Core Marketplace Loop

> **Goal:** Working end-to-end flow: Register → Post Shipment → AI Price → Bid → Win → Verify → Pay.

### 1.1 Authentication (Laravel Native)

- [ ] Create custom `users` migration: `id`, `name`, `email`, `password`, `phone`, `role` (enum: driver, shipper_personal, shipper_business, shipper_enterprise, admin), `is_verified`, `avatar`, timestamps
- [ ] Create User Eloquent model with role casting, relationships
- [ ] Create `RegisterController` (email, password, name, phone, role)
- [ ] Create `LoginController` (email + password → session)
- [ ] Create `LogoutController` (destroy session)
- [ ] Create auth middleware for role-based access (`EnsureRole`)
- [ ] Create Vue login component (`resources/js/components/Auth/LoginForm.vue`)
- [ ] Create Vue register component (`resources/js/components/Auth/RegisterForm.vue`)
- [ ] Create Blade auth pages (`resources/views/auth/login.blade.php`, `register.blade.php`)
- [ ] Seed admin user via `database/seeders/AdminSeeder.php`

### 1.2 Driver & Shipper Profiles

- [ ] Create `driver_profiles` migration: `user_id`, `license_number`, `vehicle_type`, `vehicle_registration`, `aadhaar_number`, `pan_number`, `insurance_expiry`, `verification_status`, `rating`, `total_trips`
- [ ] Create `shipper_profiles` migration: `user_id`, `company_name`, `gst_number`, `pan_number`, `subscription_tier`, `total_shipments`
- [ ] Create DriverProfile and ShipperProfile Eloquent models with User relationship
- [ ] Create profile CRUD controllers and API routes
- [ ] Create Vue profile components (driver dashboard, shipper dashboard)

### 1.3 Shipments

- [ ] Create `shipments` migration: `shipper_id`, `title`, `description`, `goods_category`, `weight_kg`, `pickup_address`, `pickup_lat`, `pickup_lng`, `dropoff_address`, `dropoff_lat`, `dropoff_lng`, `distance_km`, `vehicle_type_required`, `ai_floor_price`, `ai_estimated_min`, `ai_estimated_max`, `shipper_min_price`, `shipper_max_price`, `bidding_window` (enum: urgent_5m, standard_30m, scheduled_24h), `bidding_expires_at`, `status` (enum: draft, active, bidding, assigned, in_transit, delivered, completed, cancelled, expired), timestamps
- [ ] Create Shipment Eloquent model with relationships (belongs to shipper, has many bids)
- [ ] Create `ShipmentController` with CRUD endpoints
- [ ] Integrate AI price floor: call `POST http://localhost:8001/price-estimate` on shipment creation
- [ ] Create Google Maps distance matrix integration for auto-calculating `distance_km`
- [ ] Create Vue shipment creation form with address autocomplete
- [ ] Create Vue shipment listing with filters (status, distance, price range)
- [ ] Create Vue shipment detail view with live bid feed

### 1.4 Bidding System

- [ ] Create `bids` migration: `shipment_id`, `driver_id`, `amount`, `estimated_delivery_hours`, `notes`, `status` (enum: pending, accepted, rejected, expired), timestamps
- [ ] Create Bid Eloquent model with relationships
- [ ] Create `BidController`: place bid (validate against AI floor), list bids, accept bid
- [ ] Create `BidExpiryJob` — Laravel Queue job that fires when bidding window closes, selects lowest bid as winner
- [ ] Create `BidNotificationJob` — sends push notification to winning driver and losing bidders
- [ ] Set up Laravel Reverb for real-time bid broadcasting
- [ ] Create Vue bidding panel with countdown timer and live bid list
- [ ] Implement no-bid fallback chain (auto-notify nearby drivers, AI re-price, window extension)

### 1.5 Verification (Pickup & Delivery)

- [ ] Create `verifications` migration: `shipment_id`, `type` (enum: pickup, delivery), `otp_code`, `otp_verified_at`, `photo_url`, `verified_by_user_id`, timestamps
- [ ] Create Verification Eloquent model
- [ ] Create `VerificationController`: generate OTP, verify OTP, upload photo
- [ ] Create Vue camera capture component (pickup/delivery photo proof)
- [ ] Create Vue OTP input component

### 1.6 Payments

- [ ] Create `payments` migration: `shipment_id`, `razorpay_order_id`, `razorpay_payment_id`, `amount`, `platform_fee`, `driver_payout`, `status` (enum: pending, held, released, refunded), timestamps
- [ ] Create Payment Eloquent model
- [ ] Create `PaymentController`: create Razorpay order (escrow hold on shipment assignment)
- [ ] Create `PaymentReleaseJob` — Queue job to release payout to driver after delivery verification
- [ ] Create `PaymentWebhookController` — handle Razorpay webhook events
- [ ] Create Vue payment status component

---

## Phase 2 — Advanced Features & Intelligence

> **Goal:** Fleet management, analytics, AI improvements, and operational tooling.

### 2.1 Fleet Management

- [ ] Create `vehicles` migration: `fleet_manager_id`, `driver_id`, `registration_number`, `vehicle_type`, `capacity_kg`, `insurance_expiry`, `fitness_certificate_expiry`, `is_active`
- [ ] Create Vehicle Eloquent model
- [ ] Create fleet management dashboard (assign drivers to vehicles, track fleet utilization)
- [ ] Multi-vehicle bid assignment for fleet managers

### 2.2 Analytics & Reporting

- [ ] Create admin dashboard with Chart.js visualizations
- [ ] Shipper analytics: price history, shipment volume, cost trends
- [ ] Driver analytics: earnings, trip count, rating trends, utilization rate
- [ ] Platform analytics: GMV, active users, conversion rates, average bid counts

### 2.3 AI Model Improvements

- [ ] Train XGBoost model on historical shipment pricing data
- [ ] Implement demand surge multiplier based on corridor congestion
- [ ] Backhaul matching with geospatial polygon corridor analysis (PostGIS)
- [ ] Seasonal pricing adjustments (monsoon, harvest, festive periods)

### 2.4 Notifications & Communication

- [ ] Exotel SMS OTP integration for phone verification
- [ ] Exotel ExoPhone masked calling between driver and shipper
- [ ] Firebase Cloud Messaging push notifications
- [ ] Email notifications via Laravel Mail (Mailgun/SES driver)

---

## Phase 3 — Scale & Production Readiness

> **Goal:** Production deployment, performance optimization, and security hardening.

### 3.1 Production Deployment

- [ ] Configure Laravel Forge or Vapor for deployment
- [ ] Set up Nginx with SSL (Let's Encrypt / Caddy)
- [ ] Configure production `.env` (database pooling, Redis cluster, S3 storage)
- [ ] Set up Laravel Horizon for queue monitoring
- [ ] Set up Laravel Telescope for debugging (dev/staging only)

### 3.2 Performance

- [ ] Database indexing strategy (shipment corridors, bid lookups, user searches)
- [ ] Eloquent eager loading optimization (N+1 query prevention)
- [ ] Redis caching for hot data (active shipments, price estimates)
- [ ] Vite production build optimization (code splitting, tree shaking)

### 3.3 Security Hardening

- [ ] Rate limiting on auth and bidding endpoints
- [ ] Input sanitization and validation on all controllers
- [ ] CORS policy tightening for production domains
- [ ] Database query audit (ensure no raw SQL injection vectors)
- [ ] File upload validation (type, size, malware scanning)

### 3.4 Testing

- [ ] PHPUnit feature tests for auth flow, shipment CRUD, bidding logic
- [ ] Laravel Dusk browser tests for Vue component interactions
- [ ] API integration tests for AI microservice communication
- [ ] Load testing with Laravel's built-in HTTP client
