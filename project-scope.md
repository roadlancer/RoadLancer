# RoadLancer: AI-Powered Transportation Management System

## Problem

India's trucking industry lacks an organized marketplace, enabling **intermediaries to extract significant margin** (often 50% of shipment value) while truck drivers receive unfair prices and shippers lack market transparency.

**Current Issues:**
- Truck drivers face price volatility with no visibility into market rates
- Multiple agents create inefficiencies (e.g., ₹20K shipment → ₹10K to driver, losing ₹10K in margins)
- Low tech adoption among drivers due to literacy and complexity barriers
- Zero transparency between shippers and carriers
- ~40% of truck-km run empty (deadheading) due to no backhaul matching
- Over 9 million daily shipments affected, resulting in massive daily losses

**Result:** Both shippers and drivers lose 40-60% of transaction value to middlemen.

---

## Solution

**RoadLancer** is a direct marketplace connecting truck drivers with shippers (individuals, businesses, and enterprises), eliminating intermediaries through AI-powered pricing, transparent bidding, and secure payments.

---

## User Roles

| Role | Description | Verification |
|------|-------------|--------------|
| **Truck Driver** | Individual driver with one vehicle | License, RC, Aadhaar, PAN, Insurance — manual review by platform team |
| **Fleet Manager** | Owner-operator managing multiple vehicles and drivers | Same as driver + fleet registration documents |
| **Personal Shipper** | Individual moving personal goods (e.g., household relocation) | Aadhaar + Phone OTP |
| **Business Shipper** | SMBs with regular shipping needs | GST number + PAN |
| **Enterprise Shipper** | Large companies with high-volume, bulk shipments | GST + PAN + contract terms |
| **Platform Admin** | Internal team managing the platform | Internal access controls |

---

## Core Mechanics

### 1. Dynamic Bidding System

- Shippers list shipments with an **AI-constrained price range**
  - AI sets a **hard minimum floor** based on route distance, weight, goods type, seasonality, and demand
  - Shippers can set their range only **above** the AI floor
  - Example: AI floor = ₹14K → Shipper sets range ₹15K–₹20K → Drivers bid within ₹15K–₹20K
- **Lowest bid wins** — but the AI floor ensures drivers always earn above market-fair rates
- **Tiered bidding windows** chosen by the shipper:
  - 🔴 **Urgent**: 5 minutes
  - 🟡 **Standard**: 30 minutes
  - 🟢 **Scheduled**: Up to 24 hours
- Drivers can bid on **multiple shipments** simultaneously based on their vehicle capacity
- Fleet managers can assign different bids to different vehicles in their fleet

### 2. No-Bid Fallback Chain

If a shipment receives zero bids:
1. Platform auto-notifies nearby drivers via SMS/push with a "suggested shipment" alert
2. AI suggests a revised (higher) price range to the shipper
3. Bidding window auto-extends once
4. If still no bids → shipment expires, shipper notified to re-post

### 3. Transparent Pricing & Revenue Model

| Shipper Type | Subscription | Commission |
|--------------|-------------|------------|
| **Personal** | None | 2% per shipment |
| **Business** | First 10 shipments free/month, then ₹1,000/month for 50 listings, ₹100/additional | 2% per shipment |
| **Enterprise** | Custom pricing with volume discounts | Negotiated |

- Real-time price history and AI-driven price estimation
- No hidden margins or middlemen

### 4. Cancellation Policy

**Before bid closes:** Either party can cancel freely — no penalty.

**After a driver wins the bid:**
- **Grace period**: 15 minutes after winning — free cancellation for the driver
- **After grace period:**
  - **Financial penalty** deducted from wallet
  - **Reputation hit** on rating
  - No outright ban (no blacklist)
- **Shipper cancellation after bid is won:**
  - Same cancellation fee as drivers
  - Winning driver receives compensation

---

## Shipment Lifecycle

```
Draft → Published → Bidding Open → Bid Won → Pickup Confirmed (OTP) → In Transit → Delivered (OTP) → Payment Released → Rated
```

| State | Trigger | Notifications |
|-------|---------|---------------|
| **Draft** | Shipper creates listing | — |
| **Published** | Shipper submits listing | Nearby drivers notified |
| **Bidding Open** | Bidding window starts | All matching drivers see it |
| **Bid Won** | Lowest bid selected at window close | Winner notified (pickup details, address, payment info). Other bidders notified. |
| **Pickup Confirmed** | Driver arrives, OTP verified, photo proof of goods taken | Shipper notified |
| **In Transit** | Driver departs pickup | GPS tracking begins, shipper can track live |
| **Delivered** | Recipient provides OTP, driver uploads photo proof | Shipper notified, payment processing begins |
| **Payment Released** | 3–5 day holding period ends | Driver notified of payment (minus 2%) |
| **Rated** | Both parties rate each other | Ratings updated on profiles |

### Delivery Verification
- **Photo/video proof** of goods condition at both **pickup** and **delivery**
- **OTP confirmation** at both **pickup** and **delivery**
- Double verification protects both parties and provides evidence for disputes

---

## Payment Flow

1. **After delivery**: Shipper pays the platform (via Razorpay — UPI, cards, netbanking, wallets)
2. **Holding period**: Platform holds payment for **3–5 days**
3. **Payout**: Platform releases payment to driver, minus **2% commission**
4. **Non-payment**: If shipper doesn't pay within the defined period, platform issues a legal notice
5. **Split payments**: 2% deducted during the single payment transaction (shipper → platform → driver)

**Payment Gateway:** Razorpay (supports UPI, cards, netbanking, wallets; Route product for marketplace split payments; subscription billing for Business shippers)

---

## Pre-Bid Information Visibility

| Information | Before Bidding | After Winning |
|-------------|---------------|---------------|
| Route (city to city) | ✅ | ✅ |
| Distance | ✅ | ✅ |
| Goods category & weight | ✅ | ✅ |
| Vehicle requirements | ✅ | ✅ |
| Exact pickup/drop address | ❌ | ✅ |
| Company/shipper name | ❌ | ✅ |
| Contact info (phone/email) | ❌ | ❌ (all communication via platform) |

> **Anti-leakage measure:** Contact information is never exposed. All communication between driver and shipper goes through the platform (in-app chat + masked phone calls).

---

## Core Features

### For All Users
- **Real-time Bidding** on shipments with price transparency
- **GPS Tracking** throughout entire journey (PWA Geolocation primary + SMS-based location pings as fallback)
- **Rating System** — mutual, multi-dimensional ratings with badges and 3.5 minimum threshold
- **Payment Security** with automatic 2% fee deduction via Razorpay
- **Notification System** — WebSocket for real-time bid updates, PWA Push API for notifications, SMS (Twilio/MSG91) for offline/critical alerts
- **In-app chat + masked phone calls** (platform-generated temporary numbers, like Uber/Ola)
- **Multi-language support** — i18n built from day one, launching with Hindi + English

### For Truck Drivers
- Filter shipments by vehicle type, capacity, and route
- Dashboard showing all shipments and their status
- Document management system (License, RC, Aadhaar, PAN, Insurance)
- Bid history and earnings tracking
- Notifications with pick-up, drop-off, and payment details upon winning
- **Interactive onboarding walkthrough** on first login (big buttons, minimal text, illustrations)

### For Fleet Managers
- **Fleet Manager Dashboard** to manage all vehicles and drivers
- Assign bids to specific vehicles/drivers
- Track earnings and shipment status across the entire fleet
- Manage driver documents and compliance

### For Shippers (Personal / Business / Enterprise)
- Dashboard to manage all listings and track shipments
- View truck driver and vehicle details (not personal info like license/RC)
- Rate drivers post-completion
- Price history and bidding analytics
- Subscription-based listing management (Business/Enterprise)
- **Tiered verification**: Aadhaar (Personal), GST + PAN (Business), GST + PAN + contract (Enterprise)

### AI & Analytics
- **Price Estimation Engine** — based on distance, weight, goods type, seasonality, and demand
  - **Cold-start strategy**: Seed with government transport rate charts, fuel prices, distance matrices + manual research on 50–100 common routes. Continuously learn from platform transactions.
- **AI-enforced price floors** — prevents exploitative pricing
- **Backhaul matching** — after a driver completes delivery, AI recommends available shipments near their drop-off location to reduce empty return trips
- AI-driven recommendations for optimal pricing
- Bid pattern analysis and market insights

### Dispute Resolution
- **Automated Tier 1**: Common issues (payment delays, minor timing disputes) auto-resolved by the system
- **Human Escalation**: Complex disputes (damage claims, missing goods, conflicting delivery proof) escalated to platform support team
- GPS data, photo proof, and OTP records used as evidence

### Goods Insurance
- **Optional in-app goods insurance** via insurance partner (e.g., ICICI Lombard, Bajaj Allianz) at checkout
- Damage to goods is the driver's liability if no insurance is purchased

### Platform Administration (Admin Panel)
- User management (approve/suspend/ban drivers, shippers, fleet owners)
- Document verification queue (review uploaded driver documents)
- Dispute resolution dashboard (view and resolve escalated disputes)
- Financial dashboard (revenue, commissions, payouts, subscription status)
- Shipment monitoring (live view of all active shipments on a map)
- Analytics & reports (user growth, bid patterns, popular routes, AI model performance)
- Content management (announcements, notifications, price floor overrides)
- Blacklist & fraud management (flagged users, suspicious patterns)

---

## Communication

| Channel | Use Case |
|---------|----------|
| **In-app chat** | Async coordination (pickup instructions, delays, route changes) |
| **Masked phone calls** | Urgent coordination (platform generates a temporary number, real numbers never shared) |
| **WebSocket** | Real-time bid updates, GPS tracking |
| **PWA Push notifications** | Bid won, shipment updates, payment received |
| **SMS (Twilio/MSG91)** | Critical alerts when user is offline, OTP delivery |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5 + Django REST Framework (Python) |
| **Frontend** | Next.js 15 (TypeScript) — deployed as a Progressive Web App (PWA) |
| **Real-time** | Django Channels + Redis (WebSocket for bidding + GPS) |
| **Payments** | Razorpay (Route for split payments, Subscriptions for billing) |
| **Communication** | Exotel (SMS + OTP + masked phone calls) |
| **Push Notifications** | Firebase Cloud Messaging (FCM) via PWA service worker |
| **Database** | PostgreSQL 16 + PostGIS (geospatial) + Redis 7 (cache + broker) |
| **File Storage** | AWS S3 or Cloudflare R2 (documents + delivery photos) |
| **AI/ML** | FastAPI microservice + scikit-learn → XGBoost (pricing model) |
| **Task Queue** | Celery + Celery Beat (async processing + scheduled tasks) |
| **Hosting (MVP)** | Railway or Render (managed PaaS) |
| **DevOps** | Docker + GitHub Actions + Caddy (reverse proxy) + Sentry (monitoring) |

**Architecture:** Single Next.js app with role-based routing (`/driver/*`, `/shipper/*`, `/fleet/*`, `/admin/*`) — different layouts per role, shared auth and components.

**Authentication:** Phone + OTP as primary (via Exotel SMS). Optional email + password as secondary login for companies.

> 📄 **Full tech stack details:** See [tech-stack.md](./tech-stack.md) for architecture diagrams, library choices, project structure, and rationale.

---

## Launch Strategy

- **Corridor-first launch**: Start with a specific high-traffic route (e.g., Delhi–Mumbai or Mumbai–Pune)
- Build critical mass of both drivers and shippers in that corridor
- Expand city by city based on demand and driver network growth

---

## Development Phases

### Phase 1 — MVP (Launch)
- ✅ Authentication (Phone + OTP, role selection)
- ✅ Shipment posting (with AI price floor enforcement)
- ✅ Bidding system (tiered windows, lowest bid wins)
- ✅ Basic driver dashboard (view shipments, place bids, track status)
- ✅ Basic shipper dashboard (post shipments, view bids, track status)
- ✅ Payment integration (Razorpay, 2% commission deduction)
- ✅ Notification system (SMS + in-app)
- ✅ Delivery verification (Photo + OTP at pickup and delivery)
- ✅ i18n foundation (Hindi + English)

### Phase 2 — Core Experience
- GPS tracking (PWA Geolocation + SMS fallback)
- Rating system (multi-dimensional + badges + 3.5 threshold)
- AI pricing engine (seeded with public data, continuous learning)
- In-app chat + masked phone calls
- Admin panel (user management, document verification, disputes, financials)
- Shipper subscription management (Business tier)

### Phase 3 — Growth & Differentiation
- Fleet Manager dashboard
- AI-powered backhaul matching
- Optional goods insurance (partner integration)
- Advanced analytics & reporting
- Enterprise shipper features (custom pricing, API access)
- E-way bill integration (regulatory compliance)
- Additional language support
- Advanced badges and gamification

---

## Key Differentiators

✅ **Fair Pricing:** AI-enforced price floors eliminate exploitation — drivers always earn above market rate  
✅ **Tech-Friendly:** Interactive onboarding, big buttons, minimal text, Hindi-first, designed for low-literacy users  
✅ **Backhaul Matching:** AI recommends return loads to reduce empty trips (40% of truck-km today)  
✅ **Transparent:** No hidden margins, no contact info leakage, full shipment lifecycle visibility  
✅ **Secure:** Photo + OTP double verification, masked communication, GPS tracking  
✅ **AI-Powered:** Smart pricing, backhaul recommendations, market insights  
✅ **Scalable:** Corridor-first launch strategy, phased feature rollout  