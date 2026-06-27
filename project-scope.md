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

## Core Features

### 1. AI-Powered Price Estimation

- When a shipper creates a shipment, the system calls an AI microservice to calculate a **fair price range**
- AI considers: route distance, weight, goods category, and vehicle type
- Sets a **minimum floor price** to ensure drivers are never exploited
- Shipper sets their budget within or above the AI-suggested range

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

---

## Simplified Scope (College Project)

### What's Included ✅
- User registration & login (email/password)
- Role-based access (Driver, Shipper, Admin)
- Shipment CRUD (create, view, update status)
- AI price estimation via FastAPI microservice
- Basic bidding (place bid, accept bid)
- Shipment status tracking
- Simple OTP verification (mock — no real SMS)
- Basic dashboards with charts
- Responsive UI with Tailwind CSS

### What's NOT Included ❌ (Enterprise Features)
- Real SMS/calling integration (Exotel)
- Real payment processing (Razorpay)
- Real-time WebSocket updates
- GPS live tracking
- Fleet management
- Multi-language support (i18n)
- PostGIS geospatial queries
- Redis caching layer
- Docker containerization (optional)
- Push notifications
- Masked calling between parties

---

## Database Schema (Simplified)

### Users Table
| Column | Type | Notes |
|--------|------|-------|
| id | bigint | Primary key |
| name | string | Full name |
| email | string | Unique, for login |
| password | string | Bcrypt hashed |
| phone | string | Contact number |
| role | enum | driver, shipper, admin |
| is_verified | boolean | Account verification status |
| created_at | timestamp | |
| updated_at | timestamp | |

### Shipments Table
| Column | Type | Notes |
|--------|------|-------|
| id | bigint | Primary key |
| shipper_id | FK → users | Who created it |
| title | string | Shipment description |
| goods_category | enum | general, fragile, perishable, heavy |
| weight_kg | decimal | Cargo weight |
| pickup_address | string | Full address |
| dropoff_address | string | Full address |
| distance_km | decimal | Calculated or entered |
| vehicle_type | enum | mini_truck, medium_truck, heavy_truck |
| ai_floor_price | decimal | AI-calculated minimum |
| ai_estimated_min | decimal | AI estimated fair min |
| ai_estimated_max | decimal | AI estimated fair max |
| shipper_budget | decimal | Shipper's max budget |
| status | enum | draft, active, assigned, in_transit, delivered, completed, cancelled |
| assigned_driver_id | FK → users | Winning bidder |
| bidding_ends_at | timestamp | When bidding closes |
| created_at | timestamp | |

### Bids Table
| Column | Type | Notes |
|--------|------|-------|
| id | bigint | Primary key |
| shipment_id | FK → shipments | |
| driver_id | FK → users | |
| amount | decimal | Bid amount in INR |
| message | text | Optional note from driver |
| status | enum | pending, accepted, rejected |
| created_at | timestamp | |

### Verifications Table
| Column | Type | Notes |
|--------|------|-------|
| id | bigint | Primary key |
| shipment_id | FK → shipments | |
| type | enum | pickup, delivery |
| otp_code | string | 4-digit code |
| is_verified | boolean | |
| verified_at | timestamp | |

---

## API Endpoints (REST)

### Auth
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login (returns session) |
| POST | `/api/logout` | Logout |
| GET | `/api/user` | Get current user profile |

### Shipments
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/shipments` | List available shipments |
| POST | `/api/shipments` | Create shipment (shipper only) |
| GET | `/api/shipments/{id}` | Get shipment details |
| PUT | `/api/shipments/{id}/status` | Update shipment status |

### Bids
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/shipments/{id}/bids` | Place a bid (driver only) |
| GET | `/api/shipments/{id}/bids` | List bids for a shipment |
| PUT | `/api/bids/{id}/accept` | Accept a bid (shipper only) |

### AI Pricing
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/price-estimate` | Get AI price estimate (proxies to FastAPI) |