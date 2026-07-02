# RoadLancer — Project Memory 🧠

> **Mission:** Eliminate intermediary margins in India's trucking industry by connecting drivers with shippers through AI-powered fair pricing and transparent bidding.

> **Scope:** College-level project — simplified features, no enterprise integrations.

---

## 🏗️ 1. Architecture

Three-service architecture: **FastAPI** (Python) for business logic, **Better Auth** (Node.js) for authentication, **Vue.js 3** for frontend. All sharing a single PostgreSQL database.

### Backend (FastAPI)
- **Framework:** FastAPI (Python 3.12+)
- **ORM:** Prisma (`prisma-client-py` v0.15.0)
- **Auth:** Session-based via Bearer token → DB lookup (not JWT)
- **Middleware:** RequestLoggingMiddleware, RateLimitMiddleware (60 req/min/IP, production only)
- **AI Pricing:** scikit-learn, numpy (bundled in same service)
- **Routes:** `/api/auth` (FastAPI), `/api/admin/*`, `/api/verification/*`, `/api/shipments/*`
- **Port:** 8000

### Auth Server (Better Auth)
- **Runtime:** Node.js 20+
- **Auth Library:** Better Auth (TypeScript)
- **Database:** Prisma adapter (same PostgreSQL)
- **Prisma:** v7.x — uses `prisma-client` generator, `@prisma/adapter-pg` driver adapter, `tsx`
- **Features:** Registration, login, sessions, role-based access
- **Sessions:** Database sessions + Bearer plugin (opaque tokens, not JWT)
- **Port:** 3000

### Frontend (Vue.js)
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS 4
- **UI Library:** shadcn-vue (reka-ui primitives, Lucide icons via `@lucide/vue`)
- **Theme:** Teal (primary: `oklch(0.511 0.096 186.391)`)
- **Form Validation:** Zod v4 + manual `safeParse()` (no vuehookform)
- **Auth Client:** `better-auth` vanilla client (`baseURL: ''` for Vite proxy)
- **HTTP Client:** Axios (`@/lib/api.ts`) — centralized instance with Bearer token interceptor
- **Data Fetching:** TanStack Query (`@tanstack/vue-query`) — automatic caching, refetching, mutations
- **Router:** Vue Router with auth navigation guards
- **Composables:** `useAuth()`, `useVerificationStatus()`, `useAdminUsers()`, `usePendingUsers()`, `useVerificationList()`
- **Components:** Button, Input, Label, Card, Avatar, Badge, Separator, Tabs, Checkbox, Alert, RadioGroup
- **Layout:** Sticky NavBar, Footer, centered login card with role selection
- **Port:** 5173

---

## 🛠️ 2. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth | Better Auth (Node.js) | Production-ready, role-based, great DX |
| Backend | FastAPI (Python) | Modern, async, auto-docs, good for AI integration |
| ORM | Prisma | Type-safe, migrations, works with both Node.js and Python |
| Database | PostgreSQL 16 | Standard SQL, no PostGIS |
| Session Type | Database + Bearer | Opaque tokens verified via DB lookup, not JWT |
| UI Library | shadcn-vue | Accessible, themeable, Tailwind-native components |
| Theme | Teal | Blue-green accent for transportation/logistics branding |
| Form Validation | Zod + manual | `@vuehookform/core` incompatible with Zod v4 runtime |
| Auth Client | `better-auth` vanilla | `@better-auth/vue` removed; singleton composable pattern |
| HTTP Client | Axios | Centralized instance with Bearer token interceptor (`@/lib/api.ts`) |
| Data Fetching | TanStack Query (`@tanstack/vue-query`) | Automatic caching, refetching, and mutation support via composable hooks |
| User Roles | admin, driver, shipper | Three roles for full feature set |
| Cache | File driver | No Redis needed for local dev |
| Queue | Sync driver | Jobs run immediately, no worker process |
| Rate Limiting | Production only | `NODE_ENV=production` (auth), `ENV=production` (backend) |
| Real-time | AJAX polling (5s) | No WebSocket complexity |
| Payments | Mock | Status fields only |
| SMS/OTP | Mock | Displayed on screen, no Exotel |
| Docker | No | Runs directly on laptop |

---

## 🚦 3. Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Project Setup | ✅ Complete |
| Phase 1 | Project Restructure (Laravel → FastAPI + Better Auth) | ✅ Complete |
| Phase 2 | Better Auth Server Setup | ✅ Complete |
| Phase 3 | FastAPI Backend Setup | ✅ Complete |
| Phase 4 | Vue.js Frontend Setup (Login, NavBar, Home, Footer) | ✅ Complete |
| Phase 4.5 | Admin Dashboard, Verification Flow, TanStack Query | ✅ Complete |
| Phase 5 | Core Features (shipments, bids, verification) | ⬜ Not Started |
| Phase 6 | Polish & Presentation | ⬜ Not Started |

### E2E Test Status
- **Total tests:** 49
- **Passing:** 49
- **Flaky:** 0
- **Coverage:** Login flow, role validation, session management, admin dashboard, verification flow

### Component/Unit Test Status
- **Framework:** Vitest + @testing-library/vue + jsdom
- **Test runner:** `vitest run` (single run) or `vitest` (watch mode)
- **Location:** `frontend/src/views/__tests__/*.spec.ts` and `frontend/src/**/*.spec.ts`
- **Current tests:** AdminDashboard (17 tests)
- **Test setup:** `frontend/vitest.config.ts` (jsdom environment)

---

## 🧪 12. Component/Unit Testing Guide

### Tech Stack
| Tool | Purpose |
|------|---------|
| **Vitest** | Test runner (fast, Vite-native, ESM-first) |
| **@testing-library/vue** | Render utilities for Vue components |
| **@testing-library/dom** | DOM queries (`screen.getByText`, `screen.getByRole`, etc.) |
| **@testing-library/user-event** | Simulate user interactions (click, type, keyboard) |
| **jsdom** | Browser environment simulation (no real browser needed) |
| **@testing-library/jest-dom** | Custom matchers (`.toBeInTheDocument()`, `.toBeDisabled()`, etc.) |

### Running Tests
```bash
# From frontend/ directory
npm run test:unit          # Single run (CI mode)
npm run test:unit:watch    # Watch mode (development)
```

### Test File Location
- Co-located: `src/views/__tests__/ComponentName.spec.ts`
- Or colocated: `src/components/__tests__/ComponentName.spec.ts`
- Naming: `*.spec.ts` (not `*.test.ts` — Vitest picks up both, but project convention is `.spec.ts`)

### Writing a Component Test

#### Basic Structure
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent } from '@testing-library/vue'
import { render } from '@testing-library/vue'
import MyComponent from '../MyComponent.vue'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(MyComponent, { props: { title: 'Hello' } })
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

#### Mocking Composables (Critical Pattern)
Most components depend on composables (`useAuth()`, `useAdminUsers()`, etc.). Mock them at the module level:

```typescript
import { ref } from 'vue'
import { vi } from 'vitest'

// Mock ref values — change these in tests to control component state
const mockUser = ref<any>(null)
const mockLoading = ref(true)

vi.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    user: mockUser,
    loading: mockLoading,
  }),
}))

// In tests, control state:
mockUser.value = { id: '1', role: 'admin' }
mockLoading.value = false
```

#### Mocking Router
```typescript
const mockRouterReplace = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({
    replace: mockRouterReplace,
  }),
}))

// In tests:
expect(mockRouterReplace).toHaveBeenCalledWith('/login')
```

#### Mocking TanStack Query Composables
```typescript
const mockUsers = ref<any[]>([])
const mockLoadingUsers = ref(false)
const mockRefetchAll = vi.fn()

vi.mock('@/composables/useAdminUsers', () => ({
  useAdminUsers: () => ({
    data: mockUsers,
    isLoading: mockLoadingUsers,
    refetchAll: mockRefetchAll,
    suspendMutation: {
      mutate: vi.fn(),
      isPending: ref(false),
    },
  }),
}))
```

### Common Patterns

#### 1. Testing Redirects (watch-based)
Component uses `watch()` without `immediate: true`. Set mock values AFTER render to trigger the watcher:

```typescript
it('redirects when auth fails', async () => {
  renderDashboard()  // renders with default mock state

  // Change state AFTER render to trigger the watch
  mockAuthLoading.value = false
  mockAuthUser.value = null
  await nextTick()  // MUST wait for Vue reactivity

  expect(mockRouterReplace).toHaveBeenCalledWith('/login')
})
```

#### 2. Handling Duplicate Text (multiple elements with same text)
When the same text appears in multiple places (e.g., stats card + tab trigger), use `getAllByText`:

```typescript
// BAD — throws "Found multiple elements with the text: Drivers"
expect(screen.getByText('Drivers')).toBeInTheDocument()

// GOOD — checks at least one exists
expect(screen.getAllByText('Drivers').length).toBeGreaterThanOrEqual(1)

// BETTER — scope to specific container
const statsCard = screen.getByText('Total Users').closest('[data-slot="card"]')
expect(within(statsCard).getByText('Drivers')).toBeInTheDocument()
```

#### 3. Testing User Interactions
```typescript
import { fireEvent } from '@testing-library/vue'

it('clicks suspend button and opens dialog', async () => {
  renderDashboard()

  const row = screen.getByText('Dave Driver').closest('tr')!
  const button = row.querySelector('button')!
  await fireEvent.click(button)

  expect(screen.getByText('Suspend User')).toBeInTheDocument()
})
```

#### 4. Testing Form Inputs
```typescript
it('filters by search query', async () => {
  renderDashboard()

  const input = screen.getByPlaceholderText('Search users...')
  await fireEvent.update(input, 'alice')

  expect(screen.getByText('Alice')).toBeInTheDocument()
  expect(screen.queryByText('Bob')).not.toBeInTheDocument()
})
```

#### 5. Testing Async State Changes
```typescript
import { ref } from 'vue'
import { screen } from '@testing-library/vue'

const mockData = ref<any[]>([])

vi.mock('@/composables/useData', () => ({
  useData: () => ({ data: mockData }),
}))

it('reacts to data changes', async () => {
  renderMyComponent()

  // Initial state
  expect(screen.queryByText('Item 1')).not.toBeInTheDocument()

  // Update mock data
  mockData.value = [{ id: 1, name: 'Item 1' }]

  // Wait for Vue to re-render
  await screen.findByText('Item 1')  // auto-waits for element to appear
})
```

### Important Gotchas

1. **`watch` without `immediate`**: Values must change AFTER render to trigger. Always `await nextTick()` after changing ref values.

2. **Duplicate text**: `getByText()` throws when multiple elements match. Use `getAllByText()` or scope queries with `within()`.

3. **Mock all dependencies**: Every composable, router, and external module must be mocked. The component will crash without them.

4. **`vi.clearAllMocks()` in `beforeEach`**: Reset mock call counts between tests to avoid state leakage.

5. **Default mock state**: Set realistic defaults in `beforeEach` (e.g., authenticated admin user). Override in individual tests.

6. **`await` for async operations**: Always `await` `fireEvent.*` and `await nextTick()` after ref changes. Use `screen.findByText()` (async) instead of `screen.getByText()` (sync) when waiting for elements to appear.

7. **`screen.queryByText()` vs `screen.getByText()`**: Use `queryByText` when checking something is NOT present (returns `null` instead of throwing).

### Test Helper: renderDashboard
A shared helper wraps `@testing-library/vue`'s `render` with common stubs:

```typescript
// frontend/src/views/__tests__/renderDashboard.ts
import { render } from '@testing-library/vue'
import AdminDashboard from '../AdminDashboard.vue'

export function renderDashboard(options = {}) {
  return render(AdminDashboard, {
    ...options,
    global: {
      ...options.global,
      stubs: {
        RouterLink: { template: '<a><slot /></a>' },
        ...(options.global?.stubs || {}),
      },
    },
  })
}
```

---

## 📂 4. Reference Files

- **[project-scope.md](./project-scope.md):** Features, database schema, API endpoints.
- **[tech-stack.md](./tech-stack.md):** Technology choices with rationale.
- **[implementation-plan.md](./implementation-plan.md):** Phase-by-phase task checklist.

---

## 🔌 5. Service Ports

| Service | Port | URL | API Routes |
|---------|------|-----|------------|
| Vue.js Frontend | 5173 | http://localhost:5173 | — |
| Better Auth Server | 3000 | http://localhost:3000 | `/api/auth/*` |
| FastAPI Backend | 8000 | http://localhost:8000 | `/api/admin/*`, `/api/verification/*`, `/api/shipments/*` |
| PostgreSQL | 5433 | localhost:5433 | — |

---

## 🔐 6. Authentication System

### Overview
Authentication uses **Better Auth** (Node.js) for session management and **FastAPI** (Python) for session verification via database lookup. Sessions are **database-backed** with opaque Bearer tokens — not JWT.

### Auth Flow
```
Vue Frontend (5173)
  ↓ User selects role (driver/shipper)
  ↓ signIn.email({ email, password, name: role })
  ↓ → Vite proxy → localhost:3000/api/auth/sign-in/email
Better Auth Server (3000)
  ↓ Validates credentials against PostgreSQL
  ↓ Creates session record with opaque token
  ↓ Returns { token, user: { id, name, email, role, phone } }
  ↓ Sets HttpOnly session cookie
Frontend receives response
  ↓ Stores token via authClient.getSession() (reads cookie)
  ↓ useAuth() composable holds user state globally
  ↓ router.push('/') → NavBar shows role-based dashboard link
```

### Session Verification (FastAPI Backend)
```
Frontend sends: Authorization: Bearer <session_token>
  ↓
FastAPI dependency: get_current_user()
  ↓ Looks up session.token in DB
  ↓ Checks session.expiresAt > now
  ↓ Looks up user by session.userId
  ↓ Returns { id, email, name, role, phone }
```

### Database Schema (Auth Tables)
| Table | Purpose |
|-------|---------|
| `user` | id, name, email, emailVerified, image, role (enum), phone, suspended (bool), status (enum: pending/approved/rejected) |
| `session` | id, token (unique), expiresAt, userId, ipAddress, userAgent |
| `account` | OAuth provider accounts (not used for email/password) |
| `verification` | Email verification tokens |

### Database Schema (Business Tables — FastAPI)
| Table | Purpose |
|-------|---------|
| `shipments` | id, title, description, origin, destination, weight, status, shipperId, createdAt, updatedAt |
| `bids` | id, amount, shipmentId, driverId, status, createdAt, updatedAt |
| `user_verifications` | id, userId (unique), driver fields (nullable), shipper fields (nullable), status (enum: pending/approved/rejected), reviewedBy, reviewedAt, rejectionReason, timestamps |

### Role System
- **Enum:** `admin` | `driver` | `shipper`
- **Default:** `driver`
- **Stored as:** Prisma enum in DB, string array in Better Auth config (`type: ["admin", "driver", "shipper"]`)
- **Access:** `user.role` available in frontend after `fetchSession()`
- **Login:** User selects role via radio buttons before signing in
- **Admin access:** `admin@roadlancer.com` → `/admin` dashboard with user management

### Frontend Auth Implementation
- **Client:** `better-auth/vue` `createAuthClient({ baseURL: '' })` — empty baseURL for Vite proxy
- **Composable:** `useAuth()` — singleton pattern (lazy-init), provides `user`, `loading`, `fetchSession()`, `signOut()`
- **Router:** Vue Router with auth navigation guards (`beforeEach`)
  - `meta.requiresAuth` → redirects to `/login` if not authenticated
  - `meta.guest` → redirects to `/` if already authenticated
  - `meta.role` → redirects to `/` if user role doesn't match
- **Login:** Role radio buttons → `signIn.email()` → `fetchSession()` → validates `user.role` against selected role → `router.push('/driver'|'/shipper')` → if mismatch: generic error + sign out
- **Sign out:** `useAuth().signOut()` → `api.post('/auth/sign-out')` → clears user → `window.location.href = '/login'`
- **Verification check:** NavBar + dashboards use `useVerificationStatus()` composable — shows "Get Validated" button if not verified

### HTTP Client (Axios)
- **Instance:** `@/lib/api.ts` — centralized axios instance with Bearer token interceptor
- **Token injection:** Reads token from `authClient.getSession()`, adds `Authorization: Bearer <token>` header to every request
- **401 handling:** Redirects to `/login` on 401 response — **except** if already on `/login` (prevents redirect loop during role-mismatch sign-out)
- **All API calls** must use `api` from `@/lib/api.ts` instead of raw `fetch()` or `axios.create()`

### Data Fetching (TanStack Query)
- **Package:** `@tanstack/vue-query` (v5)
- **Plugin:** `VueQueryPlugin` added to `main.ts`
- **Pattern:** Composable hooks encapsulate query key, query function, enabled condition, and mutations
- **Shared queries:** Single composable can be used across multiple components (e.g., `useVerificationStatus()` shared by NavBar, DriverDashboard, ShipperDashboard, GetValidated)
- **Automatic invalidation:** Mutations (create, update, delete) invalidate related queries via `queryClient.invalidateQueries()`
- **Composable files:** All in `src/composables/` — `useVerificationStatus.ts`, `useAdminUsers.ts`, `usePendingUsers.ts`, `useVerificationList.ts`
- **When to use:**
  - Any `GET` request → `useQuery()`
  - Any `POST`/`PUT`/`DELETE` request → `useMutation()` + `queryClient.invalidateQueries()`
  - Shared state across components → single composable, not duplicated queries

### Backend Auth Implementation
- **Dependency:** `get_current_user(authorization: Header)` — extracts Bearer token
- **Verification:** DB lookup on `session` table → expiry check → user lookup
- **Protected routes:** `user: dict = Depends(get_current_user)` in FastAPI
- **Admin dependency:** `get_admin_user` — checks `user["role"] == "admin"`, `user["suspended"] == False`, `user["status"] == "approved"`
- **Status check:** `get_current_user` returns 403 for `suspended=True` or `status != "approved"`
- **Verification status:** `user_verifications` table tracks driver/shipper profile verification

### Backend Middleware
- **RequestLoggingMiddleware:** Logs `METHOD /path → status (duration)` for every request
- **RateLimitMiddleware:** 60 requests per IP per 60 seconds, returns 429 if exceeded — **production only** (`ENV=production`)
- **CORSMiddleware:** Allows `http://localhost:5173` with credentials

### Backend Routes
- **`/api/auth`** — Better Auth server (Node.js on port 3000)
- **`/api/admin/*`** — Admin user management (list, suspend, approve, reject)
  - `GET /api/admin/users` — list all users (with search, role filter, status filter)
  - `GET /api/admin/users/pending/list` — list pending users
  - `GET /api/admin/users/pending/count` — count pending users
  - `GET /api/admin/users/rejected/count` — count rejected users
  - `POST /api/admin/users/{id}/suspend` — suspend a user (with reason)
  - `POST /api/admin/users/{id}/unsuspend` — unsuspend a user
  - `POST /api/admin/users/{id}/approve` — approve a pending user
  - `POST /api/admin/users/{id}/reject` — reject a pending user (with reason)
- **`/api/verification/*`** — Verification submit (driver/shipper), status, admin review
  - `GET /api/verification/status` — get current user's verification status
  - `POST /api/verification/submit/driver` — submit driver verification details
  - `POST /api/verification/submit/shipper` — submit shipper verification details
  - `GET /api/verification/admin/list` — list all verification submissions (admin, with status filter + search)
  - `GET /api/verification/admin/count` — count verifications by status (admin, defaults to pending)
  - `POST /api/verification/admin/{id}/approve` — approve a verification (admin)
  - `POST /api/verification/admin/{id}/reject` — reject a verification (admin, with optional reason)
- **`/api/shipments/*`** — Shipment CRUD + bid routes (IDOR-protected)

### Frontend Composables
- **`useAuth()`** — Singleton auth state (user, loading, fetchSession, signOut)
- **`useVerificationStatus()`** — TanStack Query for verification status + submit mutation (shared by NavBar, DriverDashboard, ShipperDashboard, GetValidated)
- **`useAdminUsers()`** — TanStack Query for admin user list + suspend mutation (shared by AdminDashboard)
- **`usePendingUsers()`** — TanStack Query for pending users + approve/reject mutations (shared by PendingUsers)
- **`useVerificationList()`** — TanStack Query for admin verification list + approve/reject mutations (shared by AdminVerificationReview)

### TanStack Query Composable Pattern
```typescript
// Example: useVerificationStatus.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { computed } from 'vue'
import { api } from '@/lib/api'
import { useAuth } from './useAuth'

export function useVerificationStatus() {
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const queryKey = computed(() => ['verification-status', user.value?.id])

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      const { data } = await api.get('/verification/status')
      return data
    },
    enabled: computed(() => !!user.value && user.value.role !== 'admin'),
    staleTime: 30_000,
  })

  const submitMutation = useMutation({
    mutationFn: async (payload: { type: 'driver' | 'shipper'; data: any }) => {
      const { data } = await api.post(`/verification/submit/${payload.type}`, payload.data)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['verification-status'] })
    },
  })

  const isVerified = computed(() => query.data.value?.verified === true)
  const verificationData = computed(() => query.data.value?.verification)

  return {
    // Query state
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    // Data
    isVerified,
    verificationData,
    // Mutations
    submitVerification: submitMutation.mutate,
    isSubmitting: submitMutation.isPending,
    submitError: submitMutation.error,
  }
}
```

### Environment Variables
| Variable | Location | Value |
|----------|----------|-------|
| `DATABASE_URL` | `.env` (root) | `postgresql://postgres:postgres@localhost:5433/roadlancer` |
| `BETTER_AUTH_SECRET` | `.env` (root) | Random secret for session signing |
| `BETTER_AUTH_URL` | `.env` (auth-server) | `http://localhost:3000` |
| `TRUSTED_ORIGINS` | `.env` (root) | `http://localhost:5173` |
| `ENV` | `.env` (backend) | `production` to enable rate limiting |

### Vite Proxy Configuration
| Route | Target | Notes |
|-------|--------|-------|
| `/api/auth` | `http://localhost:3000` | Better Auth server |
| `/api/admin` | `http://localhost:8000` | FastAPI admin routes |
| `/api/shipments` | `http://localhost:8000` | FastAPI shipment routes |
| `/api/verification` | `http://localhost:8000` | FastAPI verification routes |
| `/api/me` | `http://localhost:8000` | FastAPI user info |

### Session Configuration
- **Expiry:** 7 days (`60 * 60 * 24 * 7`)
- **Update age:** 1 day (`60 * 60 * 24`) — refreshes if session is active
- **Token:** Opaque string, stored in `session.token` column

---

## 🎨 7. UI Components & Layout

### shadcn-vue Components Installed
| Component | Purpose |
|-----------|---------|
| Button | Primary actions, social login |
| Input | Email, phone, password fields |
| Label | Form field labels |
| Card | Login card, home dashboard cards |
| Avatar | User avatar with fallback |
| Badge | Role display |
| Separator | Visual dividers |
| Tabs | Email/phone login switcher |
| Checkbox | Remember me |
| Alert | Error messages |
| RadioGroup | Role selection (driver/shipper) |

### Layout Structure
- **App.vue:** `min-h-screen flex flex-col bg-background` → NavBar → `<main class="flex-1">` → Footer
- **NavBar:** Sticky (`sticky top-0 z-50 backdrop-blur-md`), role-based dashboard link, sign out button, Sign in button uses default primary teal background
- **Footer:** Brand, 3 link columns (Product, Company, Legal), social icons, copyright
- **Login:** Centered card with role radio buttons, tabs (email/phone), social login

### Theme (Teal)
- **Primary:** `oklch(0.511 0.096 186.391)` — teal blue-green
- **Primary Foreground:** `oklch(0.984 0.014 180.72)` — light teal tint
- **Charts:** Teal gradient palette (chart-1 through chart-5)
- **Dark mode:** Supported via `.dark` class

### Pages
| Route | Component | Access |
|-------|-----------|--------|
| `/` | HomeView | All authenticated users |
| `/login` | LoginView | Guest only |
| `/driver` | DriverDashboard | Driver only |
| `/shipper` | ShipperDashboard | Shipper only |
| `/get-validated` | GetValidated | Driver only |
| `/get-validated-shipper` | GetValidated | Shipper only |
| `/admin` | AdminDashboard | Admin only |
| `/admin/pending` | PendingUsers | Admin only |
| `/admin/verifications` | AdminVerificationReview | Admin only |

---

## 🔑 8. Default Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@roadlancer.com | admin123 |
| Driver | driver@roadlancer.com | driver123 |
| Shipper | shipper@roadlancer.com | shipper123 |

> **Note:** These three accounts are seeded via `auth-server/seed.ts`. All have `status=approved` by default. Old test users must be deleted from DB if found.

---

## ⚠️ 9. Known Issues & Workarounds

- **Prisma 7 (auth-server):** Requires `prisma-client` generator (not `prisma-client-js`), driver adapter (`@prisma/adapter-pg`), no `url` in schema (URL in `prisma.config.ts`)
- **Python Prisma (`prisma-client-py`):** Still requires `url` in schema
- **`@vuehookform/core`:** Incompatible with Zod v4 — `extractSubSchema` traverses `_def.checks` causing runtime crashes. Use manual `safeParse()` instead
- **Better Auth enum workaround:** `type: ["driver", "shipper"]` in `additionalFields`
- **HttpOnly cookies:** Can't read in JS — removed router guards, auth composable handles all state
- **Backend `pyproject.toml`:** Missing `[tool.setuptools.packages]` — `pip install -e .` broken; install deps individually
- **Chrome autofill:** Use `autocomplete="new-password"` on inputs to prevent yellow background
- **Auth server startup:** Must use `setsid` (not `< /dev/null`) to keep Hono alive — `process.stdin.resume()` fails when stdin is redirected
- **Vite cache:** Clear `node_modules/.vite` when changing imports (e.g., lucide-vue-next → @lucide/vue)
- **TypeScript schema indexing:** Cast `schema.shape` to `Record<string, any>` when indexing with string
- **Login role validation:** After `fetchSession()`, compare `user.role` with selected role — mismatch shows generic "Invalid credentials" error (never reveals actual role for security)
- **Old admin user:** If old admin user exists with role `driver`, login succeeds with driver radio button — delete stale users from DB
- **Seed users must have passwords:** Users created via Prisma directly have no password hash — always register via `/api/auth/sign-up/email` endpoint
- **401 interceptor login page:** Must check `window.location.pathname !== '/login'` before redirecting — prevents redirect loop when role-mismatch sign-out triggers a 401 during verification query

---

## 📁 10. Key Files

| File | Purpose |
|------|---------|
| `auth-server/auth.ts` | Better Auth config — trusted origins, Bearer plugin, role enum, rate limit (production only) |
| `auth-server/server.ts` | Hono server (port 3000) |
| `auth-server/prisma/schema.prisma` | Auth schema — enum Role, user/session/account/verification |
| `auth-server/seed.ts` | Database seeder — driver and shipper users |
| `backend/app/main.py` | FastAPI app with CORS, logging, rate limit middleware (production only) |
| `backend/app/middleware.py` | RequestLoggingMiddleware, RateLimitMiddleware |
| `backend/app/routes/auth.py` | Session-based auth via Bearer token → DB lookup |
| `backend/app/routes/admin.py` | Admin user management — list/suspend/approve/reject |
| `backend/app/routes/verification.py` | Verification submit (driver/shipper), status, admin review |
| `backend/app/routes/shipments.py` | Shipment CRUD + bid routes |
| `frontend/src/style.css` | Tailwind v4 + shadcn teal theme + autofill overrides |
| `frontend/src/router/index.ts` | Vue Router with auth + role navigation guards |
| `frontend/src/composables/useAuth.ts` | Singleton composable — exports `user`, `loading`, `fetchSession` |
| `frontend/src/composables/useVerificationStatus.ts` | TanStack Query composable — shared verification status check + submit mutation |
| `frontend/src/composables/useAdminUsers.ts` | TanStack Query composable — admin user list, suspend, pending/rejected counts |
| `frontend/src/composables/usePendingUsers.ts` | TanStack Query composable — pending user list, approve/reject mutations |
| `frontend/src/composables/useVerificationList.ts` | TanStack Query composable — admin verification list, approve/reject mutations |
| `frontend/src/lib/api.ts` | Axios instance with Bearer token interceptor and 401 redirect |
| `frontend/src/components/NavBar.vue` | Sticky nav — role dashboard link, sign out |
| `frontend/src/components/Footer.vue` | Brand, links, social icons, copyright |
| `frontend/src/views/LoginView.vue` | Role radio buttons, tabs, social login, Zod validation |
| `frontend/src/views/HomeView.vue` | Dashboard — avatar, role badge, info cards |
| `frontend/src/views/DriverDashboard.vue` | Driver-only page |
| `frontend/src/views/ShipperDashboard.vue` | Shipper-only page |
| `frontend/src/views/__tests__/AdminDashboard.spec.ts` | AdminDashboard component tests (17 tests) |
| `frontend/src/views/__tests__/renderDashboard.ts` | Shared test helper — wraps render with common stubs |

---

## 🛡️ 11. Skills

| Skill | Location | Use When |
|-------|----------|----------|
| better-auth-best-practices | `.agents/skills/better-auth-best-practices/SKILL.md` | Auth config, plugins, sessions, env vars |
| security-review | `.agents/skills/security-review/SKILL.md` | Security audit, vulnerability scan, code review |
| playwright-e2e | `.agents/skills/playwright-e2e/SKILL.md` | E2E tests, Playwright, browser tests, user flows |
| opencode customize | `<built-in>` | Editing opencode config, agents, skills, plugins |

### Using playwright-e2e

**When to use:**
- Writing new E2E test files (`.spec.ts` in `frontend/tests/`)
- Need login helpers, form testing patterns, or API interception examples
- Debugging flaky tests or setting up test fixtures

**How to use:**
1. Load the skill: `skill("playwright-e2e")`
2. Ask to write a test for a specific feature (e.g., "write a login test for driver")
3. The skill provides file templates, selector best practices, and common patterns
4. Test files go in `frontend/tests/*.spec.ts`
5. Run tests with `npm run test:e2e` from `frontend/`

**Quick commands:**
```bash
npm run test:setup         # Reset test DB + seed users
npm run test:e2e           # Run all tests (headless)
npm run test:e2e:headed    # Run with visible browser
npm run test:e2e:ui        # Open Playwright UI
```

### Component/Unit Testing Patterns

**When to use:**
- Testing individual Vue components in isolation
- Verifying UI renders correctly with different props/state
- Testing user interactions (clicks, form inputs, navigation)
- Mocking composables, router, and external dependencies

**Key patterns (see Section 12 for full guide):**
- Mock composables with `vi.mock()` at module level — control state via exported `ref()` values
- Mock router with `vi.mock('vue-router')` — assert `router.replace()` calls
- Use `getAllByText()` when text appears in multiple elements (stats cards + tab triggers)
- Set mock values AFTER `render()` to trigger `watch` without `immediate`
- Always `await nextTick()` after changing reactive refs

**Quick commands:**
```bash
npm run test:unit          # Single run
npm run test:unit:watch    # Watch mode
```

**File location:** `frontend/src/views/__tests__/*.spec.ts`
