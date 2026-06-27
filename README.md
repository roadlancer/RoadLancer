# RoadLancer 🚛

**AI-Powered Transportation Marketplace — College Project**

RoadLancer is a direct marketplace connecting truck drivers with shippers, eliminating intermediary margins through AI-powered fair pricing and transparent bidding.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Laravel 12 (PHP 8.2+) |
| **Frontend** | Blade templates + Vue.js 3 + Tailwind CSS 4 |
| **Database** | PostgreSQL 16 |
| **AI Service** | FastAPI (Python) |
| **Build Tool** | Vite |

---

## 🚀 Local Setup

### Prerequisites

- PHP 8.2+ (`sudo apt install php php-cli php-mbstring php-xml php-curl php-pgsql php-zip`)
- Composer (`curl -sS https://getcomposer.org/installer | php`)
- Node.js 20+ and npm
- PostgreSQL 16
- Python 3.11+ and uv

### Database Setup

```bash
# Create the database
sudo -u postgres psql -c "CREATE DATABASE roadlancer;"
```

### Install & Run

```bash
# 1. Install PHP dependencies
composer install

# 2. Install JS dependencies
npm install

# 3. Setup environment
cp .env.example .env
php artisan key:generate

# 4. Run database migrations and seed sample data
php artisan migrate
php artisan db:seed

# 5. Start Laravel (Terminal 1)
php artisan serve

# 6. Start Vite dev server (Terminal 2)
npm run dev

# 7. Start AI microservice (Terminal 3)
cd ai-service && uv run uvicorn app.main:app --port 8001
```

### Access

| Service | URL |
|---------|-----|
| **Application** | http://localhost:8000 |
| **AI Docs** | http://localhost:8001/docs |

### Default Accounts (after seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@roadlancer.in | password |
| Shipper | shipper@test.com | password |
| Driver | driver@test.com | password |

---

## 📂 Project Structure

```
RoadLancer/
├── app/
│   ├── Http/Controllers/    # Auth, Shipment, Bid, Admin controllers
│   ├── Models/              # User, Shipment, Bid, Verification
│   └── Services/            # AiPricingService
├── resources/
│   ├── views/               # Blade templates (layouts, auth, dashboards)
│   ├── js/                  # Vue.js 3 components
│   └── css/                 # Tailwind styles
├── routes/
│   ├── web.php              # Page routes
│   └── api.php              # REST API routes
├── database/
│   ├── migrations/          # Database schema
│   └── seeders/             # Sample data
├── ai-service/              # FastAPI AI pricing microservice
├── project-scope.md         # Feature specification
├── tech-stack.md            # Technology choices & rationale
└── implementation-plan.md   # Development task checklist
```

---

## ✨ Key Features

- 📝 User registration & login (Driver / Shipper / Admin roles)
- 📦 Shipment creation with AI-powered price estimation
- 💰 Transparent bidding system with floor price protection
- ✅ OTP-based pickup & delivery verification
- 📊 Admin dashboard with analytics charts
- 📱 Responsive design (mobile-friendly)
