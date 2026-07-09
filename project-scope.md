# RoadLancer: AI-Powered Transportation Management System

## Problem

India's trucking industry lacks an organized marketplace, enabling **intermediaries to extract significant margins** (often 40-60% of shipment value) while truck drivers receive unfair prices and shippers lack market transparency.

**Current Issues:**
- Truck drivers face price volatility with no visibility into market rates
- Multiple agents create inefficiencies (e.g., ₹20K shipment → ₹10K to driver)
- Zero transparency between shippers and carriers
- Over 9 million daily shipments affected

**Result:** Both shippers and drivers lose 40-60% of transaction value to middlemen.

---

## Solution

**RoadLancer** is a direct marketplace connecting truck drivers with shippers, eliminating intermediaries through AI-powered pricing and transparent bidding.

---

## User Roles

| Role | Description |
|------|-------------|
| **Truck Driver** | Individual driver looking for shipment jobs |
| **Shipper** | Individual or business needing goods transported |
| **Admin** | Platform administrator managing users and shipments |

---

## Architecture

Three-service architecture: **FastAPI** (Python) for business logic, **Better Auth** (Node.js) for authentication, **Vue.js 3** for frontend. All sharing a single PostgreSQL database.

| Service | Port | Tech Stack |
|---------|------|------------|
| **Backend** | 8000 | FastAPI + Prisma Python |
| **Auth Server** | 3000 | Better Auth + Hono (Node.js) |
| **Frontend** | 5173 | Vue.js 3 + Vite + Tailwind CSS 4 |
| **PostgreSQL** | 5433 | Database |

---

## Core Features

### 1. AI-Powered Price Estimation

- When a shipper creates a shipment, the system calls an AI microservice to calculate a **fair price range**
- AI considers: route distance, weight, goods category, and vehicle type
- Sets a **minimum floor price** to ensure drivers are never exploited
- Shipper sets their budget within or above the AI-suggested range
- **Forced price protection:** Shipper can override AI pricing but admins are notified

### 2. Simple Bidding System

- Drivers browse available shipments and place bids
- Bids must be at or above the AI floor price
- Shipper reviews bids and accepts the best offer
- Bidding has a time window (configurable per shipment)

### 3. Shipment Lifecycle

```
Created → Bidding Open → Bid Accepted → In Transit → Delivered → Completed
```

- Shipper creates shipment with pickup/dropoff details
- Drivers bid on available shipments
- Shipper accepts a bid → driver is assigned
- Driver marks shipment as picked up → in transit
- Driver marks shipment as delivered
- Shipper confirms delivery → shipment completed

### 4. Delivery Verification

- Simple OTP-based verification at pickup and delivery
- 4-digit code generated, shared with both parties
- Driver enters OTP to confirm pickup/delivery

### 5. User Dashboards

- **Driver Dashboard:** Available shipments, my bids, active trips, earnings history
- **Shipper Dashboard:** Create shipment, track active shipments, shipment history
- **Admin Dashboard:** Manage users, view all shipments, platform analytics

### 6. User Verification System

- Drivers submit: License, RC, Insurance, PUC documents
- Shippers submit: GST, PAN, Registration documents
- Admin reviews and approves/rejects with reasons
- Profile edit requests via support ticket workflow

### 7. Support & Inbound Email System

- Users submit support tickets with attachments
- Inbound email simulation via webhook
- Admin support desk with ticket management
- Ticket sorting by newest/oldest/priority/status

---

## Simplified Scope (College Project)

### What's Included ✅
- User registration & login (email/password)
- Role-based access (Driver, Shipper, Admin)
- Database-backed sessions (Better Auth)
- Shipment CRUD (create, view, update status)
- AI price estimation (rule-based engine, no LLM)
- Basic bidding (place bid, accept bid, upsert logic)
- Shipment status tracking
- User verification flow (document submission + admin review)
- Support ticket system with attachments
- Inbound email webhook simulation
- Basic dashboards with charts
- Responsive UI with Tailwind CSS
- Dark mode support

### What's NOT Included ❌ (Enterprise Features)
- Real SMS/calling integration (Exotel)
- Real payment processing (Razorpay)
- Real-time WebSocket updates (uses AJAX polling)
- GPS live tracking
- Fleet management
- Multi-language support (i18n)
- PostGIS geospatial queries
- Redis caching layer (uses file cache)
- Docker containerization
- Push notifications
- Masked calling between parties

---

## Database Schema

### Auth Tables (Better Auth)

#### Users Table
| Column | Type | Notes |
|--------|------|-------|
| id | text | Primary key (cuid) |
| name | string | Full name |
| email | string | Unique, for login |
| email_verified | boolean | Email verification status |
| image | string | Avatar URL (nullable) |
| role | enum | driver, shipper, admin |
| phone | string | Contact number (nullable) |
| suspended | boolean | Account suspension flag |
| status | enum | pending, approved, rejected |

#### Sessions Table
| Column | Type | Notes |
|--------|------|-------|
| id | text | Primary key |
| token | string | Unique, opaque bearer token |
| user_id | FK → users | Session owner |
| expires_at | timestamp | 7-day expiry |
| ip_address | string | Client IP |
| user_agent | string | Browser info |

### Business Tables (FastAPI)

#### Shipments Table
| Column | Type | Notes |
|--------|------|-------|
| id | int | Primary key |
| title | string | Shipment description |
| description | text | Detailed description (nullable) |
| goods_category | enum | general, fragile, perishable, heavy |
| weight_kg | decimal | Cargo weight |
| vehicle_type | enum | tempo, mini_truck, lcv, truck, multi_axle, trailer, tanker |
| pickup_address | string | Full address |
| dropoff_address | string | Full address |
| distance_km | decimal | Calculated distance |
| shipper_budget | decimal | Shipper's max budget |
| status | enum | active, assigned, picked_up, in_transit, delivered, completed, cancelled |
| shipper_id | FK → users | Who created it |
| assigned_driver_id | FK → users | Winning bidder (nullable) |
| ai_floor_price | decimal | AI-calculated minimum |
| ai_estimated_min | decimal | AI estimated fair min |
| ai_estimated_max | decimal | AI estimated fair max |
| is_forced_price | boolean | Shipper overrode AI pricing |
| created_at | timestamp | |
| updated_at | timestamp | |

#### Bids Table
| Column | Type | Notes |
|--------|------|-------|
| id | int | Primary key |
| shipment_id | FK → shipments | |
| driver_id | FK → users | |
| amount | decimal | Bid amount in INR |
| message | text | Optional note from driver |
| status | enum | pending, accepted, rejected, withdrawn |
| created_at | timestamp | |
| updated_at | timestamp | |

#### User Verifications Table
| Column | Type | Notes |
|--------|------|-------|
| id | int | Primary key |
| user_id | FK → users | Unique (one per user) |
| status | enum | pending, approved, rejected |
| reviewed_by | FK → users | Admin who reviewed (nullable) |
| reviewed_at | timestamp | When reviewed (nullable) |
| rejection_reason | text | Why rejected (nullable) |
| **Driver Fields** | | |
| driver_license_number | string | DL number |
| driver_license_photo | text | Base64 encoded |
| rc_number | string | RC number |
| rc_photo | text | Base64 encoded |
| insurance_number | string | Insurance policy |
| insurance_photo | text | Base64 encoded |
| puc_number | string | PUC certificate |
| puc_photo | text | Base64 encoded |
| driver_full_name | string | Verified name |
| driver_dob | string | Date of birth |
| driver_gender | string | Gender |
| driver_address | text | Full address |
| driver_phone | string | Contact phone |
| **Shipper Fields** | | |
| gst_number | string | GSTIN |
| gst_photo | text | Base64 encoded |
| pan_number | string | PAN number |
| pan_photo | text | Base64 encoded |
| company_name | string | Business name |
| company_address | text | Business address |
| company_phone | string | Business phone |
| company_email | string | Business email |
| company_registration | string | Registration number |
| company_registration_photo | text | Base64 encoded |

---

## API Endpoints (REST)

### Auth (Better Auth Server - Port 3000)
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/auth/sign-up/email` | Register new user |
| POST | `/api/auth/sign-in/email` | Login (returns session) |
| POST | `/api/auth/sign-out` | Logout |
| GET | `/api/auth/get-session` | Get current user session |

### Admin (FastAPI - Port 8000)
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/admin/users` | List all users (with search/filter) |
| GET | `/api/admin/users/pending/list` | List pending users |
| GET | `/api/admin/users/pending/count` | Count pending users |
| GET | `/api/admin/users/rejected/count` | Count rejected users |
| POST | `/api/admin/users/{id}/suspend` | Suspend a user |
| POST | `/api/admin/users/{id}/unsuspend` | Unsuspend a user |
| POST | `/api/admin/users/{id}/approve` | Approve a pending user |
| POST | `/api/admin/users/{id}/reject` | Reject a pending user |

### Verification (FastAPI - Port 8000)
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/verification/status` | Get current user's verification status |
| POST | `/api/verification/submit/driver` | Submit driver verification |
| POST | `/api/verification/submit/shipper` | Submit shipper verification |
| GET | `/api/verification/admin/list` | List all verifications (admin) |
| GET | `/api/verification/admin/count` | Count verifications by status |
| POST | `/api/verification/admin/{id}/approve` | Approve verification |
| POST | `/api/verification/admin/{id}/reject` | Reject verification |

### Shipments (FastAPI - Port 8000)
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/shipments` | List shipments (drivers: active; shippers: all) |
| POST | `/api/shipments` | Create shipment (shipper only) |
| GET | `/api/shipments/assigned` | Get driver's assigned shipments |
| GET | `/api/shipments/bids/my` | Get driver's bid history |
| GET | `/api/shipments/{id}` | Get shipment details |
| PUT | `/api/shipments/{id}/status` | Update shipment status |
| POST | `/api/shipments/{id}/bids` | Place a bid (driver, upsert) |
| GET | `/api/shipments/{id}/bids` | List bids (shipper only) |
| GET | `/api/shipments/{id}/bids/count` | Count bids on shipment |
| POST | `/api/shipments/{id}/bids/{bid_id}/accept` | Accept a bid (shipper only) |
| POST | `/api/shipments/estimate-price` | AI price estimation (no auth) |

### Support (FastAPI - Port 8000)
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/support/inbound-email` | Inbound email webhook simulation |
| GET | `/api/support/tickets` | List support tickets |
| GET | `/api/support/tickets/{id}` | Get ticket details |
| PUT | `/api/support/tickets/{id}/resolve` | Resolve a ticket |

---

## AI Pricing Engine

**Type:** Rule-based (no LLM API calls, fast and deterministic)

**Pricing Formula:**
```
Total Price = (Distance × Rate/km) + Weight Charge + Vehicle Multiplier + Goods Multiplier + Fuel Cost + Tolls + Labour + Seasonal Demand
```

**Distance Tiers:**
| Range | Rate/km |
|-------|---------|
| < 100 km | ₹18/km |
| 100-500 km | ₹14/km |
| 500+ km | ₹11/km |

**Weight Tiers:**
| Range | Rate/kg |
|-------|---------|
| < 500 kg | ₹0.5/kg |
| 500-2000 kg | ₹0.4/kg |
| 2000-5000 kg | ₹0.35/kg |
| 5000+ kg | ₹0.3/kg |

**Vehicle Multipliers:**
| Vehicle | Multiplier |
|---------|------------|
| Tempo | 0.8x |
| Mini Truck | 1.0x |
| LCV | 1.2x |
| Truck | 1.5x |
| Multi-Axle | 1.8x |
| Trailer | 2.2x |
| Tanker | 1.7x |

**Goods Multipliers:**
| Category | Multiplier |
|----------|------------|
| General | 1.0x |
| Electronics | 1.15x |
| Fragile | 1.2x |
| Hazmat | 1.25x |
| Cold Chain | 1.3x |
| Perishable | 1.1x |
| Bulk | 0.9x |
| Heavy Machinery | 1.4x |

**Cost Components:**
- **Fuel:** ₹90/L diesel, 4-8 km/L depending on vehicle
- **Tolls:** ₹2/km average
- **Labour:** ₹500-2000 base (varies by vehicle type)
- **Seasonal:** Peak (Oct-Mar) 1.15x, Off-peak (Apr-Sep) 0.9x

**Price Bounds:**
- Floor = 70% of calculated total
- Minimum = 85% of calculated total
- Maximum = 125% of calculated total

---

## Default Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@roadlancer.com | admin123 |
| Driver | driver@roadlancer.com | driver123 |
| Shipper | shipper@roadlancer.com | shipper123 |

> **Note:** Seeded via `auth-server/seed.ts`. All have `status=approved`.

---

## Testing

### E2E Tests (Playwright)
- **Framework:** Playwright + TypeScript
- **Location:** `frontend/tests/*.spec.ts`
- **Total tests:** 52
- **Status:** All passing

### Unit Tests (Vitest)
- **Framework:** Vitest + @testing-library/vue + jsdom
- **Location:** `frontend/src/views/__tests__/*.spec.ts`
- **Total tests:** 27 (22 passing, 5 pre-existing failures in AdminDashboard)

### Test Commands
```bash
bun run test:e2e           # Run E2E tests
bun run test:unit          # Run unit tests
```

---

## Project Status

### Completed ✅
- Authentication system (Better Auth, sessions, role-based access)
- AI pricing engine (rule-based)
- Shipment CRUD + bidding system
- User verification flow (document submission + admin review)
- Support ticket system + inbound email webhook
- All dashboards (Driver, Shipper, Admin)
- E2E test suite (52 tests)
- Unit test suite (27 tests)

### In Progress / Known Issues
- Pre-existing unit test failures in AdminDashboard (duplicate text element queries)

### Not Implemented
- OTP verification (mock only, no real SMS)
- Charts/analytics (no chart library installed)
- Phone login (UI tab exists but backend only supports email)
- Bidding countdown timer
- Sample seed data for demo
