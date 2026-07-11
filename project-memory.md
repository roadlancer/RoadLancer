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
- **Form Validation:** Zod v4 schemas + manual `safeParse()` across all form inputs (`LoginView.vue`, `GetValidated.vue`, etc. — no vuehookform) with `max()` length constraints
- **XSS Sanitization:** DOMPurify (`@/lib/sanitize.ts`) — `sanitize()` for HTML body content, `sanitizeText()` for plain text (subjects, names, addresses). Applied at composable query/mutation layer (`useSupportTickets.ts`, `useShipments.ts`, `useCreateShipment.ts`) and form emit layer (`ReplyForm.vue`).
- **Auth Client:** `better-auth` vanilla client (`baseURL: ''` for Vite proxy)
- **HTTP Client:** Axios (`@/lib/api.ts`) — centralized instance with Bearer token interceptor
- **Data Fetching:** TanStack Query (`@tanstack/vue-query`) — automatic caching, refetching, mutations
- **Router:** Vue Router with auth navigation guards
- **Composables:** `useAuth()`, `useVerificationStatus()`, `useAdminUsers()`, `usePendingUsers()`, `useVerificationList()`, `useSupportTickets()`
- **Components:** Button, Input, Label, Card, Avatar, Badge, Separator, Tabs, Checkbox, Alert, RadioGroup, UsersTable, TicketsTable (`@tanstack/vue-table` sorting & pagination)
- **Layout:** Sticky NavBar (left-aligned brand & Dashboard links, uniform h-10 primary buttons, Help & Support trigger restricted strictly to authenticated users), Footer, Admin Dashboard & Support Desk (shared navigation banner, 8 Lucide KPI cards for supreme admins / 3 for agents, search/filter headers, extracted table components, dedicated ticket resolution desk at `/admin/support/:id`), Agent Management page (`/admin/agents`), centered login card with role selection
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
| AI Pricing | Rule-based engine | Fast, free, deterministic — no LLM API costs, no latency |
| Price Confirmation | Forced price protection | Shipper can set custom price but warning visible to admins only |
| Landing Page | Public marketing page | Product introduction for new users, no auth required |
| RoadLancer Brand | Logged-out only | Hidden when logged in to reduce visual clutter |
| Footer | Removed | Simplified layout, no legal/policy requirements for college project |
| XSS Prevention | DOMPurify | `sanitize()` for HTML bodies, `sanitizeText()` for plain text; applied at composable data layer |
| Input Length Limits | Prisma `@db.VarChar` + Pydantic `Field(max_length=...)` + HTML `maxlength` + Zod `.max()` | Three-layer defense: database, backend API, frontend form |

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
| Phase 5 | Core Features (shipments, bids, AI pricing, price confirmation) | ✅ Complete |
| Phase 5.1 | Marketing Landing Page, Public Home | ✅ Complete |
| Phase 5.2 | AI Price Engine, Price Confirmation Flow | ✅ Complete |
| Phase 5.3 | Driver Bidding Flow, Bid Review, Transit Status | ✅ Complete |
| Phase 5.4 | Shipper Dashboard, Shipment Management | ✅ Complete |
| Phase 5.5 | Forced Price Protection (Admin-only visibility) | ✅ Complete |
| Phase 5.6 | Helpdesk & Support Desk UI Standardization, Ticket Sorting (`sort_by`), Auth-restricted triggers | ✅ Complete |
| Phase 5.7 | Support Desk Enhancements: TanStack Table Sorting & Pagination, Interactive Inline Agent Assignment (`[ASSIGNED_TO]`), Agent Filtering, & Dedicated Ticket Detail Page (`/admin/support/:id`) | ✅ Complete |
| Phase 5.8 | Table Customization & Verification Safeguards: Max 8 Columns Checkbox Chooser, Inline Status/Category Selects, & Approved Verification Reset Lock (`[ASSIGNED_TO]` & AI score data integrity) | ✅ Complete |
| Phase 5.9 | Support Desk Reply Threading: Dedicated ticket_replies Model (`senderRole` & `senderType` for `agent`/`customer` distinction), Auto-creation via Raw SQL (`ALTER TABLE`), Admin & User Reply Endpoints (`POST /replies`), and Interactive Discussion & Reply Form (`AdminTicketDetailView.vue`) | ✅ Complete |
| Phase 5.10 | Security Hardening: DOMPurify XSS sanitization (`@/lib/sanitize.ts`), Pydantic `Field(max_length=...)` on all request models, Prisma `@db.VarChar(...)` on `support_tickets` & `ticket_replies`, HTML `maxlength` + Zod `.max()` on frontend forms, `bodyHtml` column on `ticket_replies` | ✅ Complete |
| Phase 5.11 | Agent Management: `isSupreme` flag on user model, create/deactivate/activate agent endpoints (supreme admin only), separate admin/agent login page (`/admin/login`), agent-scoped ticket filtering (non-supreme agents only see assigned tickets), Unverified stats card, status filter cards hidden for non-supreme agents | ✅ Complete |
| Phase 5.12 | Agent UI Refinements: Agent filter dropdown hidden for sub-agents on support desk, per-row agent assignment column hidden for sub-agents, "Assigned Agent" column toggle hidden in column chooser for sub-agents, fixed deactivation bug (event handler passed userId string but treated as agent object) | ✅ Complete |
| Phase 6 | Polish & Presentation | ⬜ Not Started |

### Overall Completion: **~98%**

| Area | Completion | Notes |
|------|------------|-------|
| Auth System | 100% | Better Auth, login, sessions, role-based access, authenticated support trigger, separate admin/agent login page |
| Backend Routes | 100% | 40+ endpoints (auth, admin, users, verification with approved reset checks, shipments, bids, support/inbound-email with `sort_field`/`sort_order` sorting & single ticket GET, agent management: create/deactivate/activate with ticket unassignment). All Pydantic request models enforce `max_length` constraints. |
| AI Pricing Engine | 100% | Rule-based with all factors |
| Database Schema | 100% | 11 models implemented (incl. `support_tickets` with `VarChar` limits & `ticket_replies` with `bodyHtml`, `isSupreme` field on user model) |
| Security | 100% | DOMPurify XSS sanitization on all user-supplied content, three-layer input length enforcement (Prisma VarChar → Pydantic max_length → HTML maxlength/Zod .max()) |
| Frontend Views | 98% | 16 views (all dashboards, login (driver/shipper), admin/agent login (`/admin/login`), home, shipment detail, verification with AI checked status lock, admin support desk with agent filtering for supreme admins only, admin ticket detail view with assign-to-me, agent management with deactivation bug fix) |
| Frontend Composables | 100% | 14 composables including `useSupportAgents()`, `useAdminAgents()` for unified agent management (real DB agents only, no dummy data, deactivation with ticket unassignment) |
| Frontend Components | 100% | 11 components (`UsersTable`, `AgentsTable`, `TicketsTable` with `@tanstack/vue-table` sorting, pagination, Max 8 column visibility popover, and direct inline status/category/agent selects with sub-agent restrictions) |
| Shipment Flow | 100% | Create → Price → Bidding → Transit |
| Support & Email Webhook | 100% | Inbound email simulation, TanStack Table column sorting & custom visibility, assigned agents tracking (`[ASSIGNED_TO]`), standardized Admin Helpdesk UI & dedicated resolution page, agent-scoped ticket filtering, sub-agent UI restrictions |
| Agent Management | 100% | Create/deactivate/activate agents (supreme admin only), `isSupreme` flag, agent-scoped ticket visibility, separate login page, sub-agent UI restrictions, deactivation bug fix |
| Testing | 97% | 72 component tests passing (AdminDashboard: 29 tests incl. unverified card & non-supreme visibility, TicketsTable: 14 tests, ReplyForm: 10 tests, TicketDetail, UpdateTicket, ReplyThread) |

### What's Missing

| Item | Impact | Priority |
|------|--------|----------|
| **OTP Verification** | `verifications` table exists but no backend routes | 🟡 Important |
| **Charts/Analytics** | No chart library installed | 🟢 Nice to have |
| **Phone Login** | LoginView has phone tab but backend only supports email | 🟢 Nice to have |
| **Bidding Countdown** | `bidding_ends_at` field exists but no UI timer | 🟢 Nice to have |
| **Sample Seed Data** | No sample shipments/bids for demo | 🟢 Nice to have |

### Recently Fixed

| Item | Fix |
|------|-----|
| **Agent deactivation not working** | Event handler bug: `openDeactivateDialog` received userId string but treated as agent object. Fixed to look up full agent object from list. |
| **Sub-agent sees agent filter/assignment controls** | Hidden agent filter dropdown, per-row assignment column, and column toggle for non-supreme agents. |

### Testing Strategy

> **Core Testing Rule (Strictly Enforced):** Rely mostly on **component unit tests** (`vitest` + `@testing-library/vue`). **Remove/avoid any E2E tests that are already covered by unit tests.** Keep only those E2E tests (`playwright`) that are absolutely necessary to test full-stack functionality (such as cross-page routing, real API persistence, and browser session state) that cannot be tested with unit tests.

#### When to Use Component Tests (Primary Tool)
- Testing individual Vue components in isolation (`TicketDetail`, `UpdateTicket`, `ReplyThread`, `ReplyForm`, `TicketsTable`)
- Verifying UI renders correctly with different props, badges, and state
- Testing user interactions (clicks, form validation, inline selects, input fields)
- Mocking composables (`useAuth`, `useAdminTickets`), router, and external dependencies
- Fast feedback loop (runs in seconds on every code change)

#### When to Use E2E Tests (Strictly Necessary Full-Stack Only)
- Testing complete multi-page navigation and URL route transitions (`/admin/support` $\to$ `/admin/support/:id`)
- Testing real API integration & database persistence across views without mocks (e.g., verifying that a status update or new reply saved on the details page permanently persists when returning to the main table or reloading)
- Testing browser cookie session verification and HTTP redirect flow

#### Test Coverage Priorities
1. **High priority (component tests):** Login, dashboards, shipment creation, bidding, verification forms, support ticket detail components (`TicketDetail`, `UpdateTicket`, `ReplyThread`, `ReplyForm`)
2. **Medium priority (component tests):** Admin user management, support tickets table, price estimation dialogs
3. **Low priority (full-stack E2E only):** Multi-page route transitions (`ticket-detail-page.spec.ts`), real DB state persistence across page reloads

### E2E Test Status
- **Framework:** Playwright (Chromium headless/headed with `roadlancer_test` PostgreSQL db)
- **Scope:** Critical full-stack integration flows only (login, role validation, session management, admin verification, support webhook creation, `ticket-detail-page.spec.ts` standalone navigation & persistence across routes)
- **Rule:** No redundant UI/prop testing in E2E; exclusively full-stack integration.

### Component Test Status
- **Framework:** Vitest + @testing-library/vue + jsdom
- **Test runner:** `bunx vitest run` (single run) or `bunx vitest` (watch mode)
- **Location:** `frontend/src/views/__tests__/*.spec.ts` and `frontend/src/**/*.spec.ts`
- **Current suites:** AdminDashboard (29 tests — includes unverified card & non-supreme visibility), TicketsTable & inline assignment (14 tests), ReplyForm (10 tests), TicketDetail, UpdateTicket, ReplyThread (72 tests total, all passing)
- **Test setup:** `frontend/vitest.config.ts` (jsdom environment)

---

## 🧪 12. Component/Unit Testing Guide

> **Strategy:** Component tests are our primary testing tool. Use E2E tests ONLY for critical user flows and real backend persistence that cannot be tested with unit tests.

### Why Component Tests First?
- **Fast:** Runs in seconds, not minutes
- **Isolated:** Tests one component at a time
- **Deterministic:** No flaky tests from network/browser issues
- **Easy to debug:** Failures point to exact component
- **Mock-friendly:** Control all external dependencies

### When to Add E2E Tests
- **Critical user flows:** Login → dashboard → create shipment → bid → accept
- **Real integration:** Testing actual API calls without mocks
- **Browser behavior:** Cookies, localStorage, redirects
- **Regression prevention:** Ensuring critical paths don't break

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
bunx vitest run          # Single run (CI mode)
bunx vitest              # Watch mode (development)
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
  ↓ User navigates to /login (Driver/Shipper) or /admin/login (Admin/Agent)
  ↓ Driver/Shipper: selects role via radio buttons
  ↓ Admin/Agent: directly enters credentials
  ↓ signIn.email({ email, password, name: role })
  ↓ → Vite proxy → localhost:3000/api/auth/sign-in/email
Better Auth Server (3000)
  ↓ Validates credentials against PostgreSQL
  ↓ Creates session record with opaque token
  ↓ Returns { token, user: { id, name, email, role, phone, isSupreme } }
  ↓ Sets HttpOnly session cookie
Frontend receives response
  ↓ Stores token via authClient.getSession() (reads cookie)
  ↓ useAuth() composable holds user state globally
  ↓ Redirects to correct dashboard based on actual user.role
  ↓ (ignores selected radio — always routes /driver, /admin, or /shipper)
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
| `user` | id, name, email, emailVerified, image, role (enum), phone, suspended (bool), isSupreme (bool, default false), status (enum: pending/approved/rejected) |
| `session` | id, token (unique), expiresAt, userId, ipAddress, userAgent |
| `account` | OAuth provider accounts (not used for email/password) |
| `verification` | Email verification tokens |

### Database Schema (Business Tables — FastAPI)
| Table | Purpose |
|-------|---------|
| `shipments` | id, title, description, goodsCategory, weightKg, vehicleType, pickupAddress, dropoffAddress, distanceKm, shipperBudget, status, shipperId, assignedDriverId, aiFloorPrice, aiEstimatedMin, aiEstimatedMax, isForcedPrice, createdAt, updatedAt |
| `bids` | id, amount, message (`VarChar(1000)`), shipmentId, driverId, status (pending/accepted/rejected/withdrawn), createdAt, updatedAt |
| `user_verifications` | id, userId (unique), driver fields (nullable), shipper fields (nullable), status (enum: pending/approved/rejected), reviewedBy, reviewedAt, rejectionReason, timestamps |
| `support_tickets` | id, ticketNumber (`VarChar(20)`, unique), senderEmail (`VarChar(255)`), senderName (`VarChar(100)`), subject (`VarChar(200)`), message (`VarChar(5000)`), category (`VarChar(50)`), status (`VarChar(20)`), priority (`VarChar(20)`), source (`VarChar(20)`), userId, adminNotes (`VarChar(2000)`), createdAt, updatedAt |
| `ticket_replies` | id, ticketId (FK → support_tickets), senderName (`VarChar(100)`), senderRole (`VarChar(20)`: admin/user), senderType (`VarChar(20)`: agent/customer), message (`VarChar(5000)`), bodyHtml (`VarChar(10000)`, optional — sanitized HTML), createdAt |

### Shipment Status Flow
```
active → assigned → picked_up → in_transit → delivered → completed
active → cancelled
assigned → cancelled (only by shipper)
```

### Role System
- **Enum:** `admin` | `driver` | `shipper`
- **Default:** `driver`
- **Stored as:** Prisma enum in DB, string array in Better Auth config (`type: ["admin", "driver", "shipper"]`)
- **Access:** `user.role` available in frontend after `fetchSession()`
- **Login:** User selects role via radio buttons before signing in
- **Admin access:** `admin@roadlancer.com` → `/admin` dashboard with user management
- **`isSupreme` flag:** Boolean on user model — grants supreme admin privileges (agent management, status filter cards on dashboard). Set to `true` for `QzLwskaA83cgHMKnAZ45r1U76bYXZSLl` in DB.
- **Agent management:** Supreme admins can create/deactivate/activate admin agents via `/admin/agents` page. Agents have `role: admin` but `isSupreme: false`.
- **Agent-scoped tickets:** Non-supreme agents only see tickets assigned to them via `[ASSIGNED_TO:agentId|]` tag in `adminNotes`.
- **Sub-agent UI restrictions:** Non-supreme agents do not see the agent filter dropdown, per-row agent assignment column, or "Assigned Agent" column toggle on the support desk. These controls are only visible to supreme admins.
- **Separate login pages:** Regular login (`/login`) for Driver/Shipper; Admin/Agent login (`/admin/login`) for admin role.

### Frontend Auth Implementation
- **Client:** `better-auth/vue` `createAuthClient({ baseURL: '' })` — empty baseURL for Vite proxy
- **Composable:** `useAuth()` — singleton pattern (lazy-init), provides `user`, `loading`, `fetchSession()`, `signOut()`
- **Router:** Vue Router with auth navigation guards (`beforeEach`)
  - `meta.requiresAuth` → redirects to `/login` if not authenticated
  - `meta.guest` → redirects to `/` if already authenticated
  - `meta.role` → redirects to `/` if user role doesn't match
- **Login:** Role radio buttons → `signIn.email()` → `fetchSession()` → redirects to `/driver`, `/admin`, or `/shipper` based on `user.role` (radio selection is ignored for routing). Regular login (`/login`) for Driver/Shipper only; Admin/Agent login (`/admin/login`) for admin role.
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
- **`/api/admin/*`** — Admin user management (list, suspend, approve, reject) + agent management (supreme admin only)
  - `GET /api/admin/users` — list all users (with search, role filter, status filter)
  - `GET /api/admin/users/pending/list` — list pending users
  - `GET /api/admin/users/pending/count` — count pending users
  - `GET /api/admin/users/rejected/count` — count rejected users
  - `POST /api/admin/users/{id}/suspend` — suspend a user (clears `[ASSIGNED_TO]` from tickets)
  - `POST /api/admin/users/{id}/unsuspend` — unsuspend a user
  - `POST /api/admin/users/{id}/approve` — approve a pending user
  - `POST /api/admin/users/{id}/reject` — reject a pending user (with reason)
  - `POST /api/admin/users/{id}/deactivate-agent` — deactivate admin agent (supreme admin only, sets `suspended: True`, deletes sessions, clears `[ASSIGNED_TO]` from all assigned tickets making them unassigned)
  - `POST /api/admin/users/{id}/activate-agent` — activate admin agent (supreme admin only, sets `suspended: False`)
  - `POST /api/admin/users/create-agent` — create new admin agent account (supreme admin only, with scrypt password hashing)
- **`/api/verification/*`** — Verification submit (driver/shipper), status, admin review
  - `GET /api/verification/status` — get current user's verification status
  - `POST /api/verification/submit/driver` — submit driver verification details
  - `POST /api/verification/submit/shipper` — submit shipper verification details
  - `GET /api/verification/admin/list` — list all verification submissions (admin, with status filter + search)
  - `GET /api/verification/admin/count` — count verifications by status (admin, defaults to pending)
  - `POST /api/verification/admin/{id}/approve` — approve a verification (admin, automatically syncs user table name/phone)
  - `POST /api/verification/admin/{id}/reject` — reject a verification (admin, with optional reason)
  - `POST /api/verification/admin/{id}/reset-pending` — soft-reset a verification record back to pending (admin utility for re-verification)
  - `POST /api/verification/admin/reset-all-pending` — soft-reset all verification records back to pending (admin utility for testing without hard deletion)
- **`/api/shipments/*`** — Shipment CRUD + bid routes (IDOR-protected)
  - `GET /api/shipments` — list shipments (drivers see active; shippers see all their shipments)
  - `POST /api/shipments` — create shipment (with AI pricing)
  - `GET /api/shipments/assigned` — get driver's assigned shipments
  - `GET /api/shipments/bids/my` — get driver's bid history
  - `GET /api/shipments/{id}` — get shipment details
  - `PUT /api/shipments/{id}/status` — update shipment status (validated flow)
  - `POST /api/shipments/{id}/bids` — place a bid (driver)
  - `GET /api/shipments/{id}/bids` — list bids (shipper only, IDOR)
  - `GET /api/shipments/{id}/bids/count` — count bids on a shipment
  - `POST /api/shipments/{id}/bids/{bid_id}/accept` — accept a bid (shipper only)
  - `POST /api/shipments/estimate-price` — AI price estimation (no auth required)
- **`/api/support/*`** — Support tickets & inbound email webhook (sorted newest first by default, with `sort_field` and `sort_order` support for TanStack Table). Agent-scoped filtering for non-supreme agents via `[ASSIGNED_TO:agentId|]` tag. All string inputs validated with Pydantic `Field(max_length=...)` constraints.
  - `POST /api/support/inbound-email` — inbound email webhook simulation (auto-creates tickets, links to sender account if matched). Enforces: subject ≤200, body ≤5000, senderName ≤100, email ≤255.
  - `POST /api/support/tickets` — create web support ticket (`user: dict = Depends(get_current_user)`). Enforces: subject ≤200, message ≤5000.
  - `GET /api/support/tickets/my` — get current user's tickets (supports status/source filters + search + column sorting via `sort_field`/`sort_order`)
  - `GET /api/support/admin/list` — list all support tickets (admin only, supports filters + search + column sorting via `sort_field`/`sort_order`). Non-supreme agents only see tickets assigned to them via `[ASSIGNED_TO:agentId|]` tag.
  - `GET /api/support/admin/count` — get KPI counts (`total`, `open`, `in_progress`, `resolved`, `closed`, `inbound_email`, `web`). Non-supreme agents see only their assigned ticket counts.
  - `GET /api/support/admin/{ticket_id}` — get single support ticket by ID or `ticketNumber` (admin only). Non-supreme agents can only access their assigned tickets.
  - `PUT /api/support/admin/{ticket_id}/status` — update ticket workflow status, priority ranking, and internal resolution notes (`adminNotes ≤2000`) including assigned agent metadata (admin only)
  - `POST /api/support/admin/{ticket_id}/replies` — admin reply (message ≤5000, senderName ≤100)
  - `POST /api/support/tickets/{ticket_id}/replies` — user reply (message ≤5000)

### AI Pricing Engine

**File:** `backend/app/services/pricing.py`

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

**Forced Price Flow:**
1. Shipper fills all shipment fields
2. Clicks "Check Price" → calls `POST /api/shipments/estimate-price`
3. PriceConfirmDialog shows AI suggested range
4. Shipper can use suggested price OR set custom price
5. If custom price < 80% of floor price → error warning shown
6. If shipper still insists → checkbox acknowledgment required
7. Marked as `is_forced_price: true` in database
8. Badge visible to admins only on ShipmentDetailView

### Frontend Composables
- **`useAuth()`** — Singleton auth state (user, loading, fetchSession, signOut)
- **`useVerificationStatus()`** — TanStack Query for verification status + submit mutation (shared by NavBar, DriverDashboard, ShipperDashboard, GetValidated)
- **`useAdminUsers()`** — TanStack Query for admin user list + suspend mutation (shared by AdminDashboard)
- **`usePendingUsers()`** — TanStack Query for pending users + approve/reject mutations (shared by PendingUsers)
- **`useVerificationList()`** — TanStack Query for admin verification list + approve/reject mutations (shared by AdminVerificationReview)
- **`useAdminAgents()`** — TanStack Query for admin agent list + create/deactivate/activate mutations (real DB agents only, no dummy data, deactivation clears `[ASSIGNED_TO]` from tickets)
- **`useShipments()`** — TanStack Query for shipment list (drivers see active, shippers see all their shipments)
- **`useCreateShipment()`** — Mutation for creating new shipments
- **`useShipmentDetail()`** — TanStack Query for single shipment details
- **`useShipmentBids()`** — TanStack Query for shipment bids (shipper view)
- **`usePlaceBid()`** — Mutation for drivers to place bids
- **`useAcceptBid()`** — Mutation for shippers to accept bids
- **`useUpdateShipmentStatus()`** — Mutation for updating shipment status (validated flow)
- **`usePriceEstimate()`** — Mutation for AI price estimation (no auth required)

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
| Badge | Role display, status badges |
| Separator | Visual dividers |
| Tabs | Email/phone login switcher |
| Checkbox | Remember me, forced price acknowledgment |
| Alert | Error messages, price warnings |
| RadioGroup | Role selection (driver/shipper) |
| Select | Vehicle type, goods category selection |
| Dialog | Price confirmation, bid review |
| Textarea | Shipment description |
| Collapsible | Price breakdown details |
| ScrollArea | Bid list scroll |

### Layout Structure
- **App.vue:** `min-h-screen flex flex-col bg-background` → NavBar → `<main class="flex-1">` (no Footer)
- **NavBar:** Sticky (`sticky top-0 z-50 backdrop-blur-md`), role-based dashboard link, sign out button, RoadLancer brand only visible when logged out, Dashboard text font size increased. Admin nav links cleaned up — only Dashboard and Document Verification remain (Support Desk and Agent Mgmt moved to AdminDashboard header).
- **Footer:** Removed from all pages
- **Login:** Centered card with role radio buttons, tabs (email/phone), social login. Regular login (`/login`) for Driver/Shipper only; Admin/Agent login (`/admin/login`) for admin role. "Admin / Agent? Login here" link at bottom of regular login page.
- **Home:** Public marketing landing page (no auth required)

### Theme (Teal)
- **Primary:** `oklch(0.511 0.096 186.391)` — teal blue-green
- **Primary Foreground:** `oklch(0.984 0.014 180.72)` — light teal tint
- **Charts:** Teal gradient palette (chart-1 through chart-5)
- **Dark mode:** Supported via `.dark` class

### Pages
| Route | Component | Access |
|-------|-----------|--------|
| `/` | HomeView (Marketing Landing) | Public (all users) |
| `/login` | LoginView (Driver/Shipper only) | Guest only |
| `/admin/login` | AdminLoginView (Admin/Agent) | Guest only |
| `/driver` | DriverDashboard | Driver only |
| `/shipper` | ShipperDashboard | Shipper only |
| `/shipments/:id` | ShipmentDetailView | Authenticated users |
| `/get-validated` | GetValidated | Driver or Shipper (dynamic form) |
| `/admin` | AdminDashboard | Admin only |
| `/admin/profile` | AdminProfile | Admin only |
| `/admin/pending` | PendingUsers | Admin only |
| `/admin/verifications` | AdminVerificationReview | Admin only |
| `/admin/support` | AdminSupportDesk | Admin only (agent filter & assignment controls visible to supreme admins only) |
| `/admin/support/:id` | AdminTicketDetailView | Admin only |
| `/admin/agents` | AdminAgentManagement | Supreme admin only |

---

## 🚚 7.5 Shipment & Bidding Flow

### Shipper Flow
```
1. Click "Create Shipment" on ShipperDashboard
2. Fill all fields (title, goods category, weight, pickup/dropoff, vehicle type)
3. Click "Check Price" → AI pricing engine calculates suggested range
4. PriceConfirmDialog shows:
   - AI Floor Price, Suggested Price, Maximum Price
   - Option: "Use Suggested Price" or "Set Custom Price"
   - If custom < 80% of floor → error warning (cannot proceed)
   - If custom ≥ 80% of floor but < floor → warning + checkbox acknowledgment
5. Confirm → Shipment created with `is_forced_price` flag if applicable
6. Wait for drivers to place bids
7. Review bids → Accept best bid → Driver assigned
8. Track transit status on ShipmentDetailView
9. Mark as completed when delivered
```

### Driver Flow
```
1. View available shipments on DriverDashboard
2. Click "View Details" → ShipmentDetailView
3. Click "Submit Bid" → BidSubmissionDialog
4. Enter bid amount (must be within shipper's minimum and maximum price limits)
5. Submit → Shipper reviews
6. If accepted → Shipment assigned to you
7. Update status: Confirm Pickup → In Transit → Delivered
8. Shipper marks as completed
```

### Admin Visibility
- Admin sees all shipments in system
- Admin sees "Forced Price" badge on shipments where shipper overrode AI pricing
- Admin can view shipment details, bids, and status history

---

## 🔑 8. Default Accounts

| Role | Email | Password | Notes |
|------|-------|----------|-------|
| Admin | admin@roadlancer.com | admin123 | `isSupreme=true` |
| Driver | driver@roadlancer.com | driver123 | |
| Shipper | shipper@roadlancer.com | shipper123 | |
| Agent | john@roadlancer.com | johndoe17# | `role: admin`, `isSupreme=false` — sub-agent created via Agent Management |

> **Note:** Admin and Agent accounts have `role=admin`. The three base accounts are seeded via `auth-server/seed.ts`. Agent account created via `/api/admin/users/create-agent` endpoint. All have `status=approved` by default. Old test users must be deleted from DB if found.

---

## ⚠️ 9. Known Issues & Workarounds

- **Prisma 7 & Python Prisma (`prisma-client-py`):** In Prisma 7 CLI, `url` is no longer supported inside `datasource db` in `schema.prisma`. Remove `url` from `schema.prisma`, configure `prisma.config.ts` for migrations/generation, and pass `datasource={'url': os.environ.get('DATABASE_URL')}` directly to the `Prisma()` constructor in Python (`backend/app/database.py`).
- **`@vuehookform/core`:** Incompatible with Zod v4 — `extractSubSchema` traverses `_def.checks` causing runtime crashes. Use manual `safeParse()` instead
- **Better Auth enum workaround:** `type: ["driver", "shipper"]` in `additionalFields`
- **HttpOnly cookies:** Can't read in JS — removed router guards, auth composable handles all state
- **Backend `pyproject.toml`:** Missing `[tool.setuptools.packages]` — `pip install -e .` broken; install deps individually
- **Chrome autofill:** Use `autocomplete="new-password"` on inputs to prevent yellow background
- **Auth server startup:** Must use `setsid` (not `< /dev/null`) to keep Hono alive — `process.stdin.resume()` fails when stdin is redirected
- **Backend startup:** Must use `setsid` and plain `uvicorn app.main:app --port 8000` (without `--reload`) — with reload it starts then shuts down immediately.
- **Backend password hashing (scrypt):** better-auth uses scrypt (N=16384, r=16, p=1, dkLen=64). Salt is 16 random bytes hex-encoded, then the **hex string itself** (not decoded bytes) is passed as UTF-8 to scrypt. Python must match: `salt_hex.encode("utf-8")` as salt input, NOT `bytes.fromhex(salt_hex)`. Hash format: `{hex_salt}:{hex_key}`.
- **Backend Prisma client must be regenerated** (`prisma generate`) after schema changes for Python client to recognize new fields like `isSupreme`.
- **Vite proxy order:** Specific routes (e.g., `/api/auth`) must come before catch-all routes. If using a single `/api` → backend catch-all, ensure auth routes are handled separately. The auth server (port 3000) and backend (port 8000) share the same `/api` prefix via Vite proxy.
- **Vite cache:** Clear `node_modules/.vite` when changing imports (e.g., lucide-vue-next → @lucide/vue)
- **TypeScript schema indexing:** Cast `schema.shape` to `Record<string, any>` when indexing with string
- **Login role validation:** After `fetchSession()`, login redirects to the correct dashboard based on the user's actual role (`/driver`, `/admin`, or `/shipper`), regardless of which role radio button was selected. Previously showed "Invalid credentials" on role mismatch — now removed for better UX.
- **Old admin user:** If old admin user exists with role `driver`, login succeeds with driver radio button — delete stale users from DB
- **Seed users must have passwords:** Users created via Prisma directly have no password hash — always register via `/api/auth/sign-up/email` endpoint
- **401 interceptor login page:** Must check `window.location.pathname !== '/login'` before redirecting — prevents redirect loop when role-mismatch sign-out triggers a 401 during verification query
- **Prisma Python (`prisma-client-py`) Limitations:** Does not support `select` or `include` keyword arguments in `find_unique` or `find_many`. Use `db.query_raw(...)` when selective projection or joins are required, and ensure raw date/time strings from SQL queries are properly handled before calling `.isoformat()`.
- **Prisma Python Enums:** Generated models wrap enum fields in Python `Enum` objects; access them via `.value` when comparing strings or serializing to JSON.
- **Admin Dashboard Card Stats / Tab Filtering:** In `useAdminUsers()`, always fetch all users without filtering by `role` on the backend so that client-side stats across all 8 summary cards never drop to 0 when clicking an individual card. Admin users are excluded client-side in `AdminDashboard.vue` (`filteredUsers` and `stats` computed).
- **Admin Users Excluded from User Management:** Admin users (including agents) are filtered out of the user table and stats cards in `AdminDashboard.vue`. Admins are managed via the dedicated Agent Management page (`/admin/agents`) for supreme admins only.
- **Unverified Stats Card:** The "Unverified" card counts users with `verification_status === 'none'` (registered but never submitted verification documents). This is computed client-side from the user list — no separate API endpoint needed.
- **Non-Supreme Agent Card Visibility:** Status-based filter cards (Unverified, Verified, Pending, Rejected, Suspended) are only visible to supreme admins (`user?.isSupreme`). Non-supreme agents only see Total Users, Drivers, and Shippers cards.
- **No Direct Profile Edits for Admins:** For compliance and traceability, Admins should never arbitrarily edit verified driver or shipper profile data directly on the dashboard. Changes must strictly follow a user-initiated support ticket/email trail.
- **Strict Soft Deletion / Suspension:** Never implement hard delete (`DELETE FROM ...`) endpoints for user accounts or verification records. Always use soft deletion (such as setting verification status to `rejected` or account status to `suspended`) to preserve audit trails, fraud logs, and historical traceability.
- **Profile Edit Request Workflow:** When a verified driver or shipper needs to update their profile data, they must click "Request Profile Edit / Update" on their verification page and provide a support ticket reference / reason. This unlocks their form, submits an edit request (`isEditRequest: true`), sets their verification status back to `pending`, and flags the reason as `[PROFILE EDIT REQUEST]` for Admin review. When Admin approves, the user's main `user` table record (`name` and `phone`) is automatically synchronized.
- **Agent Deactivation Event Handler Bug:** `AgentsTable.vue` emits `'deactivate'` with `row.original.id` (a string), but `AdminAgentManagement.vue`'s `openDeactivateDialog` treated the parameter as an agent object. Then `confirmDeactivate` tried `agentToDeactivate.value.id` which was `undefined` on a string, so the API was never called. Fixed by having `openDeactivateDialog` look up the full agent object from the agents list by userId.
- **Sub-Agent UI Restrictions:** Non-supreme agents (sub-agents) should not see agent-related controls on the support desk. The agent filter dropdown, per-row agent assignment column, and "Assigned Agent" column toggle in the column chooser are all hidden for non-supreme users via `v-if="user?.isSupreme"` checks in `AdminSupportDesk.vue` and `TicketsTable.vue`.
- **Shipment List Logic:** Backend `GET /api/shipments` returns ALL active shipments for drivers (not filtered by status). For shippers, it returns all their shipments (active, completed, cancelled) so they can see history.
- **Status Update Validation:** Backend validates status transitions. Drivers can only update to: picked_up, in_transit, delivered. Shippers can only update to: completed, cancelled.
- **AI Pricing is Rule-Based:** No LLM API calls — fast, free, deterministic. Diesel price fixed at ₹90/L. Tolls estimated at ₹2/km. Labour base ₹500-2000 by vehicle type.
- **Forced Price Visibility:** `is_forced_price` flag is only visible to admins on ShipmentDetailView. Drivers and shippers cannot see this flag.
- **Estimate Price Endpoint:** `POST /api/shipments/estimate-price` requires no authentication — called before shipment creation to show price range.
- **TanStack Query / Vue Query Reactivity (`@tanstack/vue-query`):** When passing getter functions or reactive values to `useQuery` (e.g., `shipmentId`), always wrap `queryKey` and `enabled` in Vue `computed(() => ...)` properties. If passed as plain static arrays or booleans, they evaluate once on component creation and freeze forever (causing dialogs or child components mounted with initially null props to get permanently stuck with `enabled: false`).
- **Prisma Python Relation Join Conflicts / Include Errors:** In `prisma-client-py`, querying models with `include={"relationName": True}` can fail with internal query errors if relation names conflict across models (e.g., `@relation("Driver")` on both `bids.driver` and `user.assignedShipments`). Since frontend serializers (`bid_to_dict`, `shipment_to_dict`) only require scalar foreign key IDs (`driver_id`, `shipment_id`), avoid unnecessary `include` arguments on `find_many` calls.
- **Prisma Engine Warm-Up Required:** On first query after server start, Prisma's Rust engine binary can segfault. Add a warm-up query in the FastAPI lifespan that runs `await db.query_raw('SELECT 1')` with retry logic (3 attempts with exponential backoff) before the server marks itself as ready.
- **Pending Login & Action Restriction Workflow:** Users with `pending` status are permitted to log in and access dashboards/verification pages without triggering 403 errors in `get_current_user`. Instead, functionality restriction is applied at the action layer: backend endpoints that modify state (`create_shipment`, `place_bid`, `accept_bid`, `update_shipment_status`) check `if user.get("status") != "approved"` and raise 403. In the UI, dashboards display an amber warning banner prompting verification submission and visually disable action buttons.
- **Resolved SPA Navigation Freezes:** Vue Router would occasionally freeze during dev (HMR) or reactive state synchronization when navigating between dashboards and the verification forms. To ensure maximum reliability and bypass complex reactive route guards, navigation links across the NavBar, Dashboards, and Profiles have been converted to native HTML `<a>` tags, forcing a clean browser navigation.
- **Admin Verification Data Parity:** The "Review Docs" modal in the Admin User Table originally showed empty credentials because it passed a stub object. It now fetches the full, authoritative data from `/api/verification/admin/list` before opening, ensuring it exactly matches the data model of the dedicated Verification Review page.
- **Bid Upsert Logic:** The POST `/api/shipments/{id}/bids` endpoint intelligently acts as an upsert. If a driver has already placed a bid, it will update their existing bid rather than throwing a 400 error, allowing seamless quote revisions from the UI without complex POST/PUT conditionals.
- **ShipperDashboard Shipments:** The frontend blindly trusts the backend's `list_shipments` endpoint to return ONLY the shipper's own shipments. Redundant frontend filtering by `shipper_id` has been removed to prevent hydration mismatches or typos (e.g. `shipperId` vs `shipper_id`) from hiding valid shipments.
- **Seeded User Names:** Test users seeded via `auth-server/seed.ts` use "Driver User", "Shipper User", "Admin User" as display names (not "Test Driver" etc.). When writing Playwright tests, match exact names or use regex patterns scoped to `[role="dialog"]` to avoid strict mode violations from duplicate matches.
- **`openBidReviewDialog` → `openBidReview` Function Name Mismatch:** In `ShipperDashboard.vue`, the template referenced `openBidReviewDialog` but the function was defined as `openBidReview` (line 259). Fixed by renaming the function definition to match the template reference.
- **DriverDashboard Missing `verificationStatus` Destructuring:** In `useVerificationStatus()` call, `verificationStatus` was not included in the destructuring. Fixed by adding `status: verificationStatus` to the destructured variables.
- **`AdminTicketDetailView` Fallback Fetching:** The query `useAdminTicket(ticketId)` calls `GET /api/support/admin/{ticket_id}` to retrieve individual ticket details. If the backend instance has not been reloaded or returns an error, the query gracefully catches the exception and falls back to searching `GET /api/support/admin/list` (`SupportTicket[]`) by `id` or `ticket_number`, ensuring zero downtime or broken views during active development.
- **Assigned Agent Metadata inside `admin_notes`:** To track assigned support agents (`agentId`, `agentName`) without requiring breaking schema migrations on the `support_tickets` table, `parseAssignedAgent` and `formatAssignedAgentNotes` (`useSupportTickets.ts`) store assigned agent information directly inside the `adminNotes` text column using the structured prefix tag `[ASSIGNED_TO:id|name]\n<clean_notes>`.
- **`@tanstack/vue-table` Column Sorting Synchronization:** In `TicketsTable.vue`, column sorting state (`SortingState`) is bound via `v-model:sorting` to `AdminSupportDesk.vue`, which watches changes and updates `sortField` and `sortOrder` in `useAdminTickets()`. The backend `sort_tickets_list()` utility checks `sort_field` first (supporting sorting across `ticket_number`, `sender_email`, `subject`, `source`, weighted `priority`, weighted `status`, and `created_at`), overriding legacy `sort_by` options when active.
- **Support Table Column Customization & Layout Stability (`Max 8 Columns` Limit):** As more interactive elements (category selects, status dropdowns, priority rankings, assigned agent dropdowns) are added to TanStack tables (`TicketsTable.vue`), displaying too many columns simultaneously causes horizontal squishing and layout disruption. To maintain visual balance without removing required data, `TicketsTable.vue` implements an interactive **Column Visibility Chooser (`columnVisibility` state)** with checkboxes and an enforced **Maximum 8 Columns limit (`visibleColumnCount <= 8`)**. By default, secondary fields like `Created At` are hidden to preserve clean 8-column layout integrity.
- **Approved Verification Reset Safeguards:** When a driver or shipper application is approved by an admin, their document credentials have already undergone automated AI score checking and human verification. To prevent accidental resets or disrupting verified user accounts, the *"Reset to Pending"* action (`POST /verification/admin/{id}/reset-pending`) explicitly blocks resetting `approved` verifications (`HTTP 400`). Furthermore, bulk admin reset endpoints (`POST /verification/admin/reset-all-pending`) explicitly filter by `where={"status": "rejected"}`, ensuring that global testing/reset utilities only target rejected applications.

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
| `backend/app/database.py` | Prisma client initialization |
| `backend/app/routes/auth.py` | Session-based auth via Bearer token → DB lookup |
| `backend/app/routes/admin.py` | Admin auth dependency (`get_admin_user`, `get_supreme_admin_user`) |
| `backend/app/routes/users.py` | User management endpoints — list, suspend, pending, approve, reject + agent management (create/deactivate/activate) |
| `backend/app/routes/verification.py` | Verification submit (driver/shipper), status, admin review |
| `backend/app/routes/support.py` | Support ticket endpoints (with sort_by support for newest/oldest/priority/status) & inbound email webhook parser simulation |
| `backend/app/routes/shipments.py` | Shipment CRUD, bids, status updates, AI pricing |
| `backend/app/services/pricing.py` | AI-based pricing engine — rule-based with distance, weight, vehicle, goods, fuel, labour, seasonal factors |
| `backend/prisma/schema.prisma` | Business schema — shipments, bids, user_verifications |
| `frontend/src/style.css` | Tailwind v4 + shadcn teal theme + autofill overrides |
| `frontend/src/router/index.ts` | Vue Router with auth + role navigation guards |
| `frontend/src/composables/useAuth.ts` | Singleton composable — exports `user`, `loading`, `fetchSession` |
| `frontend/src/composables/useVerificationStatus.ts` | TanStack Query composable — shared verification status check + submit mutation |
| `frontend/src/composables/useAdminUsers.ts` | TanStack Query composable — admin user list, suspend, pending/rejected counts |
| `frontend/src/composables/usePendingUsers.ts` | TanStack Query composable — pending user list, approve/reject mutations |
| `frontend/src/composables/useVerificationList.ts` | TanStack Query composable — admin verification list, approve/reject mutations |
| `frontend/src/composables/useShipments.ts` | TanStack Query composable — shipment list query |
| `frontend/src/composables/useCreateShipment.ts` | TanStack Query composable — create shipment mutation |
| `frontend/src/composables/useShipmentDetail.ts` | TanStack Query composable — shipment detail, bids, assigned queries |
| `frontend/src/composables/usePlaceBid.ts` | TanStack Query composable — place bid mutation |
| `frontend/src/composables/useAcceptBid.ts` | TanStack Query composable — accept bid mutation |
| `frontend/src/composables/useUpdateShipmentStatus.ts` | TanStack Query composable — status update mutation |
| `frontend/src/composables/usePriceEstimate.ts` | TanStack Query composable — AI price estimation mutation |
| `frontend/src/composables/useSupportTickets.ts` | TanStack Query composable — support tickets (`sort_field`/`sort_order` sorting, `useAdminTicket`), inbound email simulation, assigned agent parsers (`[ASSIGNED_TO]`), and admin helpdesk |
| `frontend/src/composables/useAdminAgents.ts` | TanStack Query composable — admin agent list, create/deactivate/activate mutations (real DB agents only) |
| `frontend/src/lib/api.ts` | Axios instance with Bearer token interceptor and 401 redirect |
| `frontend/src/components/NavBar.vue` | Sticky nav — RoadLancer brand only when logged out, Help & Support trigger restricted strictly to authenticated users |
| `frontend/src/components/Footer.vue` | Brand, links, social icons, copyright |
| `frontend/src/components/UsersTable.vue` | Extracted admin user management table component with role/status badges and suspend actions |
| `frontend/src/components/TicketsTable.vue` | `@tanstack/vue-table` support ticket & inbound email table matching UsersTable design with clickable headers for sorting, Max 8 Column Visibility Chooser (`columnVisibility` popover with "Assigned Agent" toggle hidden for sub-agents), interactive inline status/category/agent selects (agent column hidden for sub-agents), pagination controls, and row click navigation to `/admin/support/:id` |
| `frontend/src/components/VerificationDetailDialog.vue` | Detailed dossier inspection modal displaying user profile fields, attached document images (Aadhaar, DL, RC, Insurance, GST, PAN), status badges, and action controls with approved verification reset lock |
| `frontend/src/components/FileUpload.vue` | Reusable image upload component for Base64 document attachments with thumbnail preview & validation |
| `frontend/src/components/CreateShipmentDialog.vue` | Shipment creation form with all fields (title, goods, weight, pickup/dropoff, vehicle) |
| `frontend/src/components/PriceConfirmDialog.vue` | Price confirmation pop-up — AI suggested range, custom price input, forced price warning |
| `frontend/src/components/BidSubmissionDialog.vue` | Driver bid submission with floor price validation |
| `frontend/src/components/BidReviewDialog.vue` | Shipper bid review/accept interface |
| `frontend/src/components/SupportEmailSimulatorModal.vue` | Interactive helpdesk modal for simulating inbound emails to support@roadlancer.com and viewing tickets |
| `frontend/src/views/LoginView.vue` | Role radio buttons, tabs, social login, Zod validation (Driver/Shipper only). "Admin / Agent? Login here" link at bottom. |
| `frontend/src/views/GetValidated.vue` | Multi-section accordion verification forms for Driver (DL, RC, Insurance, PUC) and Shipper (GST, PAN, Reg) with Base64 photo uploads |
| `frontend/src/views/AdminVerificationReview.vue` | Admin review interface displaying expanded profile fields, document inspection lightbox, and rejection reasons |
| `frontend/src/views/HomeView.vue` | Public marketing landing page — Hero, How It Works, Features, Stats, Trust Signals, CTA |
| `frontend/src/views/DriverDashboard.vue` | Driver dashboard — assigned shipments tab, bid history, external links |
| `frontend/src/views/ShipperDashboard.vue` | Shipper dashboard — KPIs, shipment list, create/review buttons |
| `frontend/src/views/ShipmentDetailView.vue` | Shipment detail — status timeline, bid management, transit actions, AI price estimate |
| `frontend/src/views/AdminDashboard.vue` | Admin dashboard — compact stats cards (including Unverified card for users who haven't applied), role filtering & sorting selects, user table (admins excluded), forced price badge. Status-based cards and agent management link hidden for non-supreme agents. |
| `frontend/src/views/AdminSupportDesk.vue` | Dedicated admin helpdesk view matching AdminDashboard UI (shared gradient header with Agent Management link for supreme admins, 7 Lucide KPI cards, unified search/filter header with agent filter hidden for sub-agents, `@tanstack/vue-table` sorting sync, modal inspect/reply desk, agent assignment controls hidden for sub-agents) |
| `frontend/src/views/AdminTicketDetailView.vue` | Dedicated ticket inspection & resolution page (`/admin/support/:id`) displaying subject, linked profile verification, priority & status badges, assigned agent selection (`[ASSIGNED_TO:id|name]`), quick resolve button, and internal notes |
| `frontend/src/views/AdminLoginView.vue` | Separate admin/agent login page at `/admin/login` |
| `frontend/src/views/AdminAgentManagement.vue` | Agent management page at `/admin/agents` (supreme admin only) — create/deactivate/activate agents with confirmation dialog, deactivation clears `[ASSIGNED_TO]` from tickets |
| `frontend/src/components/AgentsTable.vue` | Agent management table with deactivate/activate actions (activate button shown for suspended agents) |
| `frontend/src/views/__tests__/AdminDashboard.spec.ts` | AdminDashboard component tests (29 tests — includes unverified card, non-supreme visibility) |
| `frontend/src/views/__tests__/renderDashboard.ts` | Shared test helper — wraps render with common stubs |
| `frontend/src/components/__tests__/TicketsTable.spec.ts` | TicketsTable & column customization unit test suite (table layout without sender column, inline agent/status/category select events, and Suite 6 Max 8 Column Chooser checkbox UX assertions) |

---

## 🛡️ 11. Skills

| Skill | Location | Use When |
|-------|----------|----------|
| better-auth-best-practices | `.agents/skills/better-auth-best-practices/SKILL.md` | Auth config, plugins, sessions, env vars |
| security-review | `.agents/skills/security-review/SKILL.md` | Security audit, vulnerability scan, code review |
| playwright-e2e | `.agents/skills/playwright-e2e/SKILL.md` | E2E tests, Playwright, browser tests, user flows |
| opencode customize | `<built-in>` | Editing opencode config, agents, skills, plugins |

### Using playwright-e2e

**When to use (limited scope):**
- Writing E2E tests for critical user flows only
- Testing complete login → dashboard → action flows
- Verifying real API integration without mocks
- Debugging flaky component tests that need real browser

**When NOT to use:**
- Testing individual components (use Vitest instead)
- Testing business logic (use Vitest instead)
- Testing UI rendering (use Vitest instead)
- Quick feedback during development (use Vitest instead)

**How to use:**
1. Load the skill: `skill("playwright-e2e")`
2. Ask to write a test for a specific feature (e.g., "write a login test for driver")
3. The skill provides file templates, selector best practices, and common patterns
4. Test files go in `frontend/tests/*.spec.ts`
5. Run tests with `bun run test:e2e` from `frontend/`

**Quick commands:**
```bash
bun run test:setup         # Reset test DB + seed users
bun run test:e2e           # Run all tests (headless)
bun run test:e2e:headed    # Run with visible browser
bun run test:e2e:ui        # Open Playwright UI
```

### Component/Unit Testing Patterns (Primary Approach)

**When to use (preferred):**
- Testing individual Vue components in isolation
- Verifying UI renders correctly with different props/state
- Testing user interactions (clicks, form inputs, navigation)
- Mocking composables, router, and external dependencies
- Fast feedback loop during development

**Key patterns (see Section 12 for full guide):**
- Mock composables with `vi.mock()` at module level — control state via exported `ref()` values
- Mock router with `vi.mock('vue-router')` — assert `router.replace()` calls
- Use `getAllByText()` when text appears in multiple elements (stats cards + tab triggers)
- Set mock values AFTER `render()` to trigger `watch` without `immediate`
- Always `await nextTick()` after changing reactive refs

**Quick commands:**
```bash
bun run test:unit          # Single run (uses bunx vitest run)
bun run test:unit:watch    # Watch mode
```

**File location:** `frontend/src/views/__tests__/*.spec.ts`

---

## 📊 13. Completion Summary

### What's Done (93%)

#### Recently Completed
| Feature | Status | Details |
|---------|--------|---------|
| Agent UI Refinements | ✅ | Agent filter dropdown hidden for sub-agents, per-row agent assignment column hidden for sub-agents, "Assigned Agent" column toggle hidden in column chooser for sub-agents, fixed deactivation bug (event handler passed userId string but treated as agent object) |

#### Core Features
| Feature | Status | Details |
|---------|--------|---------|
| Auth System | ✅ | Better Auth server, login, sessions, role-based access, seed data, separate admin/agent login page |
| Backend Routes | ✅ | 40+ endpoints (auth, admin, users, verification, shipments, bids, support/inbound-email, agent management with ticket unassignment) |
| AI Pricing Engine | ✅ | Rule-based with distance/weight/vehicle/goods/fuel/labour/seasonal factors |
| Database Schema | ✅ | 11 models (users, sessions, shipments, bids, verifications, support_tickets, ticket_replies, `isSupreme` field) |
| Frontend Views | ✅ | 16 views (all dashboards, login pages, home, shipment detail, verification, admin support desk with sub-agent restrictions, admin ticket detail view, agent management) |
| Frontend Composables | ✅ | 14 composables (all TanStack Query-based, including `useAdminAgents` with deactivation/ticket unassignment) |
| Frontend Components | ✅ | 11 components (dialogs, UsersTable, AgentsTable, TicketsTable with `@tanstack/vue-table` and sub-agent restrictions, forms, nav, support email simulator) |
| Shipment Flow | ✅ | Create → AI pricing → Price confirm → Bidding → Accept → Transit |
| Support & Email Webhook | ✅ | Inbound email simulation converted to tickets with `@tanstack/vue-table` column sorting, assigned agents (`[ASSIGNED_TO]`), account linking, standardized Admin Helpdesk UI, & dedicated ticket resolution view (`/admin/support/:id`) with sub-agent UI restrictions |
| Forced Price Protection | ✅ | Shipper override with admin-only visibility |
| Marketing Landing Page | ✅ | Public home page with features, how-it-works, stats |
| User Registration | ✅ | Driver and Shipper registration with Zod validation & pending admin approval flow |
| Agent Management | ✅ | Create/deactivate/activate agents (supreme admin only), `isSupreme` flag, agent-scoped ticket visibility, sub-agent UI restrictions, deactivation bug fix |
| Testing | ✅ | 72 component tests passing (AdminDashboard: 29 tests, TicketsTable: 14 tests, ReplyForm: 10 tests, others) |

### What's Pending (~7%)

#### Critical for Demo
| Item | Impact | Effort |
|------|--------|--------|
| **OTP Verification** | `verifications` table exists but no backend routes | 4-6 hours |
| **Charts/Analytics** | No chart library installed | 3-4 hours |

#### Nice to Have
| Item | Impact | Effort |
|------|--------|--------|
| Phone-based login | LoginView has phone tab but backend only supports email | 2-3 hours |
| Bidding countdown timer | `bidding_ends_at` field exists but no UI timer | 1-2 hours |
| Sample seed data | No sample shipments/bids for demo | 1-2 hours |

### Recently Fixed
| Item | Fix |
|------|-----|
| **Agent deactivation not working** | Event handler bug: `openDeactivateDialog` received userId string but treated as agent object. Fixed to look up full agent object from list. |
| **Sub-agent sees agent filter/assignment controls** | Hidden agent filter dropdown, per-row assignment column, and column toggle for non-supreme agents. |

### Phase Progress

```
Phase 0 (Setup)           ✅ 100%
Phase 1 (Restructure)     ✅ 100%
Phase 2 (Auth Server)     ✅ 100%
Phase 3 (FastAPI Backend) ✅ 95%  (missing OTP routes)
Phase 4 (Vue Frontend)    ✅ 95%  (missing charts/analytics)
Phase 5 (Core Features)   ✅ 100% (missing OTP verification)
Phase 5.11 (Agent Mgmt)   ✅ 100% (isSupreme, agent CRUD, login separation, agent-scoped tickets)
Phase 5.12 (Agent UI)     ✅ 100% (sub-agent UI restrictions, deactivation bug fix)
Phase 6 (Polish)          ⬜ 0%   (not started)
```

### Recommendation

**For college demo:** The core shipment + bidding + pricing + registration + agent management flow is fully functional with proper sub-agent UI restrictions. The remaining pieces (OTP, charts) are nice enhancements but not critical for demonstrating the main value proposition.

**Recent improvements:**
1. Agent deactivation now properly unassigns tickets from the deactivated agent
2. Sub-agents no longer see confusing agent filter/assignment controls on the support desk
3. Activate button properly appears for deactivated agents

**Next steps (in order):**
1. Add charts/analytics (3-4 hours) — improves dashboard visual appeal
2. Add OTP verification (4-6 hours) — completes the shipment lifecycle
3. Add sample seed data (1-2 hours) — makes demo more realistic
4. Add component tests for remaining views (2-3 hours) — ShipperDashboard, DriverDashboard, GetValidated

**Testing strategy going forward:**
- Write component tests first for new features
- Add E2E tests only for critical user flows
- Run `bun run test:unit` on every code change
- Run `bun run test:e2e` only before demos/presentations

**Key testing areas for recent changes:**
- Agent deactivation flow (deactivate → ticket unassignment → activate)
- Sub-agent UI restrictions (hidden controls for non-supreme agents)
- Column chooser behavior with sub-agent restrictions
