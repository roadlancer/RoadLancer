---
name: playwright-e2e
description: Write and run Playwright E2E tests for RoadLancer. Use when users mention Playwright, e2e tests, end-to-end tests, browser tests, or need to test user flows like login, registration, navigation, or form submissions.
---

# Playwright E2E Testing Guide

Write and maintain end-to-end tests for RoadLancer (Vue.js 3 + Better Auth + FastAPI + PostgreSQL).

---

## Project Structure

```
frontend/
├── playwright.config.ts          # Playwright configuration
├── .env.test                     # Test environment variables
├── tests/
│   ├── global-setup.ts           # DB reset, migrations, seeding
│   └── global-teardown.ts        # Truncate test tables
```

---

## Overview

Playwright is set up with a **separate test database** (`roadlancer_test`) on the same PostgreSQL instance. The test DB is dropped, recreated, migrated, and seeded fresh before each test run.

### Configuration
| File | Purpose |
|------|---------|
| `frontend/playwright.config.ts` | Playwright config — Chromium only, auto-starts all 3 services with test DB |
| `frontend/.env.test` | Test environment variables — `DATABASE_URL` points to `roadlancer_test` |
| `frontend/tests/global-setup.ts` | Resets test DB, runs migrations, seeds users (direct DB insert with scrypt hashing) |
| `frontend/tests/global-teardown.ts` | Truncates all test tables via psql |
| `.gitignore` | Ignores `test-results/`, `playwright-report/`, `.auth/` |

### Test Database
| Property | Value |
|----------|-------|
| Name | `roadlancer_test` |
| Port | 5433 |
| Tables | `_prisma_migrations`, `user`, `account`, `session`, `verification`, `shipments`, `bids`, `verifications` |
| Seeded users | `driver@roadlancer.com` / `driver123`, `shipper@roadlancer.com` / `shipper123` |

### How It Works
1. `global-setup.ts` drops and recreates `roadlancer_test`
2. Runs auth-server migrations via `prisma migrate deploy` (creates `_prisma_migrations` table)
3. Pushes backend schema via `prisma db push` (creates business tables)
4. Seeds users via direct SQL insert with scrypt-hashed passwords (same algorithm as Better Auth)
5. Playwright starts auth-server, FastAPI, and Vite with test DB env vars
6. Tests run against the test DB
7. `global-teardown.ts` truncates all tables

### Key Decisions
- **Direct DB seeding** instead of API calls — `globalSetup` runs before `webServer` starts, so auth server isn't available
- **scrypt hashing** — matches Better Auth's password algorithm (N=16384, r=16, p=1, dkLen=64)
- **`migrate deploy`** for auth-server — tracks migrations in `_prisma_migrations`
- **`db push`** for backend — no migrations exist yet, just syncs schema state

---

## Quick Start

```bash
cd frontend
npm run test:setup         # Reset test DB + seed users
npm run test:e2e           # Run tests (headless)
npm run test:e2e:headed    # Run with visible browser
npm run test:e2e:ui        # Open Playwright UI
```

---

## Test Database

- **Name:** `roadlancer_test`
- **Port:** 5433
- **Credentials:** `postgres` / `postgres`
- **Seeded users:**
  - `driver@roadlancer.com` / `driver123` (role: driver)
  - `shipper@roadlancer.com` / `shipper123` (role: shipper)

---

## Writing Tests

### File Location
All test files go in `frontend/tests/` with `.spec.ts` extension.

### Basic Test Structure
```typescript
import { test, expect } from "@playwright/test";

test.describe("Feature Name", () => {
  test("should do something", async ({ page }) => {
    await page.goto("/some-route");
    await expect(page.locator("selector")).toBeVisible();
  });
});
```

### Authentication in Tests
Better Auth uses HttpOnly cookies — cookies are sent automatically by Playwright. To log in:

```typescript
test("authenticated flow", async ({ page }) => {
  // Navigate to login
  await page.goto("/login");

  // Select role
  await page.getByRole("radio", { name: /driver/i }).click();

  // Fill credentials
  await page.getByLabel(/email/i).fill("driver@roadlancer.com");
  await page.getByLabel(/password/i).fill("driver123");

  // Submit
  await page.getByRole("button", { name: /sign in/i }).click();

  // Wait for redirect
  await page.waitForURL("/driver");

  // Now perform authenticated actions...
});
```

### Helper: Login Fixture
Create `tests/helpers/auth.ts` for reusable login:

```typescript
import { Page, expect } from "@playwright/test";

type Role = "driver" | "shipper";

const credentials: Record<Role, { email: string; password: string }> = {
  driver: { email: "driver@roadlancer.com", password: "driver123" },
  shipper: { email: "shipper@roadlancer.com", password: "shipper123" },
};

export async function loginAs(page: Page, role: Role) {
  await page.goto("/login");
  await page.getByRole("radio", { name: new RegExp(role, "i") }).click();
  await page.getByLabel(/email/i).fill(credentials[role].email);
  await page.getByLabel(/password/i).fill(credentials[role].password);
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.waitForURL(`/${role}`);
}
```

Use in tests:
```typescript
import { loginAs } from "./helpers/auth";

test("shipper creates shipment", async ({ page }) => {
  await loginAs(page, "shipper");
  // ... test shipment creation
});
```

---

## Common Patterns

### Wait for Navigation
```typescript
await page.waitForURL("/driver");
await page.waitForLoadState("networkidle");
```

### Check Toast/Alert Messages
```typescript
await expect(page.getByText("Success message")).toBeVisible();
```

### Form Validation Errors
```typescript
await page.getByRole("button", { name: /submit/i }).click();
await expect(page.getByText("Field is required")).toBeVisible();
```

### API Interception
```typescript
await page.route("/api/shipments", (route) => {
  route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([{ id: "1", title: "Test Shipment" }]),
  });
});
```

### Loading States
```typescript
await expect(page.getByText("Loading...")).toBeVisible();
await expect(page.getByText("Loading...")).not.toBeVisible();
```

---

## Selectors (Best Practices)

### Prefer role-based selectors
```typescript
page.getByRole("button", { name: /submit/i })
page.getByRole("link", { name: /dashboard/i })
page.getByRole("radio", { name: /driver/i })
page.getByRole("textbox", { name: /email/i })
```

### Then label-based
```typescript
page.getByLabel(/password/i)
page.getByLabel(/phone number/i)
```

### Then text-based
```typescript
page.getByText("Welcome back")
page.getByText("Invalid credentials", { exact: true })
```

### Avoid
```typescript
// Don't use CSS selectors for test logic
page.locator(".btn-primary")  // ❌
page.locator("#login-form")   // ❌
```

---

## Test Data Management

### Test DB is reset before each run
`global-setup.ts` drops and recreates `roadlancer_test`, runs migrations, and seeds users. Every test run starts clean.

### Creating test data in tests
Use the API directly or interact with the UI:
```typescript
// Via API
await request.post("/api/shipments", {
  data: { title: "Test Shipment", ... },
  headers: { Authorization: `Bearer ${token}` },
});

// Via UI
await loginAs(page, "shipper");
await page.click("text=Create Shipment");
await page.fill('[name="title"]', "Test Shipment");
```

---

## Debugging

### headed mode
```bash
npm run test:e2e:headed
```

### Playwright UI mode
```bash
npm run test:e2e:ui
```

### Playwright Inspector
```bash
PWDEBUG=1 npx playwright test
```

### Screenshots on failure
Already configured in `playwright.config.ts`:
```typescript
use: {
  screenshot: "only-on-failure",
  trace: "on-first-retry",
}
```

View traces: `npx playwright show-trace test-results/.../trace.zip`

---

## Configuration Reference

### playwright.config.ts
| Setting | Value | Notes |
|---------|-------|-------|
| `testDir` | `./tests` | All `.spec.ts` files |
| `workers` | `1` | Sequential (stable for DB tests) |
| `retries` | `0` (local), `2` (CI) | |
| `browser` | Chromium only | |
| `baseURL` | `http://localhost:5173` | |
| `webServer` | 3 processes | auth:3000, api:8000, vite:5173 |
| `globalSetup` | `tests/global-setup.ts` | Reset DB + seed |
| `globalTeardown` | `tests/global-teardown.ts` | Truncate tables |

### .env.test
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/roadlancer_test
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=test-secret-key-for-e2e-only
TRUSTED_ORIGINS=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Auth server not running | `webServer` starts it automatically; if standalone, run `npm run test:setup` first |
| Stale Vite cache | `rm -rf node_modules/.vite` then restart |
| Tests flaky | Check `waitForURL` / `waitForLoadState` usage |
| `user` table reserved word | PostgreSQL requires `"user"` with double quotes |
| Login fails in test | Verify test DB has seeded users: `PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d roadlancer_test -c 'SELECT email FROM "user";'` |

---

## File Templates

### Login Test
```typescript
import { test, expect } from "@playwright/test";

test.describe("Login", () => {
  test("driver can login with valid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("radio", { name: /driver/i }).click();
    await page.getByLabel(/email/i).fill("driver@roadlancer.com");
    await page.getByLabel(/password/i).fill("driver123");
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL("/driver");
    await expect(page.getByText(/welcome/i)).toBeVisible();
  });

  test("shows error for invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("radio", { name: /driver/i }).click();
    await page.getByLabel(/email/i).fill("wrong@email.com");
    await page.getByLabel(/password/i).fill("wrongpass");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page.getByText("Invalid credentials")).toBeVisible();
  });
});
```

### Navigation Test
```typescript
import { test, expect } from "@playwright/test";

test("NavBar shows correct links for driver", async ({ page }) => {
  // Login as driver first
  await page.goto("/login");
  await page.getByRole("radio", { name: /driver/i }).click();
  await page.getByLabel(/email/i).fill("driver@roadlancer.com");
  await page.getByLabel(/password/i).fill("driver123");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.waitForURL("/driver");

  // Check NavBar
  await expect(page.getByRole("link", { name: /dashboard/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /sign out/i })).toBeVisible();
});
```
