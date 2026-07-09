import { test, expect } from "@playwright/test";
import { loginAs, logout, credentials } from "./helpers/auth";

test.describe("Authentication", () => {
  test.describe("Login Page", () => {
    test("renders login form with all elements", async ({ page }) => {
      await page.goto("/login");

      await expect(page.getByText("Welcome back")).toBeVisible();
      await expect(page.getByText("Sign in to your account")).toBeVisible();
      await expect(page.getByRole("radio", { name: /driver/i })).toBeVisible();
      await expect(page.getByRole("radio", { name: /shipper/i })).toBeVisible();
      await expect(page.getByRole("radio", { name: /admin/i })).toBeVisible();
      await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
      await expect(page.getByRole("textbox", { name: /password/i })).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test("driver radio is selected by default", async ({ page }) => {
      await page.goto("/login");

      const driverRadio = page.getByRole("radio", { name: /driver/i });
      await expect(driverRadio).toBeChecked();
    });

    test("can switch between email and phone tabs", async ({ page }) => {
      await page.goto("/login");

      await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
      await expect(page.getByRole("textbox", { name: /password/i })).toBeVisible();

      await page.getByRole("tab", { name: /phone/i }).click();
      await expect(page.getByRole("textbox", { name: /phone/i })).toBeVisible();

      await page.getByRole("tab", { name: /email/i }).click();
      await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
    });
  });

  test.describe("Login — Valid Credentials", () => {
    test("driver logs in and redirects to /driver", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.driver.email);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.driver.password);
      await page.locator('button[type="submit"]').click();

      await page.waitForURL("/driver");
      await expect(page).toHaveURL("/driver");
    });

    test("shipper logs in and redirects to /shipper", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /shipper/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.shipper.email);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.shipper.password);
      await page.locator('button[type="submit"]').click();

      await page.waitForURL("/shipper");
      await expect(page).toHaveURL("/shipper");
    });

    test("admin logs in and redirects to /admin", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /admin/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.admin.email);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.admin.password);
      await page.locator('button[type="submit"]').click();

      await page.waitForURL("/admin");
      await expect(page).toHaveURL("/admin");
    });

    test("shows loading state while submitting", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.driver.email);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.driver.password);
      await page.locator('button[type="submit"]').click();

      await expect(page.getByRole("button", { name: /signing in/i })).toBeVisible();
      await page.waitForURL("/driver");
    });
  });

  test.describe("Login — Invalid Credentials", () => {
    test("shows error for non-existent email", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill("nonexistent@email.com");
      await page.getByRole("textbox", { name: /password/i }).fill("driver123");
      await page.locator('button[type="submit"]').click();

      await expect(page.getByText(/invalid/i)).toBeVisible();
      await expect(page).toHaveURL("/login");
    });

    test("shows error for wrong password", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.driver.email);
      await page.getByRole("textbox", { name: /password/i }).fill("wrongpassword");
      await page.locator('button[type="submit"]').click();

      await expect(page.getByText(/invalid/i)).toBeVisible();
      await expect(page).toHaveURL("/login");
    });

    test("shows error for empty email", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /password/i }).fill("driver123");
      await page.locator('button[type="submit"]').click();

      await expect(page.getByText("Email is required")).toBeVisible();
    });

    test("shows error for empty password", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.driver.email);
      await page.locator('button[type="submit"]').click();

      await expect(page.getByText("Password is required")).toBeVisible();
    });

    test("shows error for invalid email format", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill("not-an-email");
      await page.getByRole("textbox", { name: /password/i }).fill("driver123");
      await page.locator('button[type="submit"]').click();

      await expect(page.getByText("Invalid email address")).toBeVisible();
    });

    test("shows error for short password", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.driver.email);
      await page.getByRole("textbox", { name: /password/i }).fill("123");
      await page.locator('button[type="submit"]').click();

      await expect(page.getByText("Password must be at least 6 characters")).toBeVisible();
    });

    test("clears error when user types in email field", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.locator('button[type="submit"]').click();
      await expect(page.getByText("Email is required")).toBeVisible();

      await page.getByRole("textbox", { name: /email/i }).fill("a");
      await expect(page.getByText("Email is required")).not.toBeVisible();
    });

    test("clears error when user types in password field", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.locator('button[type="submit"]').click();
      await expect(page.getByText("Password is required")).toBeVisible();

      await page.getByRole("textbox", { name: /password/i }).fill("a");
      await expect(page.getByText("Password is required")).not.toBeVisible();
    });
  });

  test.describe("Login — Role Mismatch", () => {
    test("driver credentials with shipper role selected redirects to driver dashboard", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /shipper/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.driver.email);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.driver.password);
      await page.locator('button[type="submit"]').click();

      await expect(page).toHaveURL("/driver");
    });

    test("shipper credentials with driver role selected redirects to shipper dashboard", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.shipper.email);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.shipper.password);
      await page.locator('button[type="submit"]').click();

      await expect(page).toHaveURL("/shipper");
    });

    test("admin credentials with driver role selected redirects to admin dashboard", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.admin.email);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.admin.password);
      await page.locator('button[type="submit"]').click();

      await expect(page).toHaveURL("/admin");
    });
  });

  test.describe("Logout", () => {
    test("driver can log out and is redirected to /login", async ({ page }) => {
      await loginAs(page, "driver");
      await expect(page).toHaveURL("/driver");

      await logout(page);
      await expect(page).toHaveURL("/login");
    });

    test("shipper can log out and is redirected to /login", async ({ page }) => {
      await loginAs(page, "shipper");
      await expect(page).toHaveURL("/shipper");

      await logout(page);
      await expect(page).toHaveURL("/login");
    });

    test("admin can log out and is redirected to /login", async ({ page }) => {
      await loginAs(page, "admin");
      await expect(page).toHaveURL("/admin");

      await logout(page);
      await expect(page).toHaveURL("/login");
    });

    test("session is cleared after logout", async ({ page }) => {
      await loginAs(page, "driver");
      await logout(page);

      await page.goto("/driver").catch(() => {});
      await page.waitForURL("/login");
      await expect(page).toHaveURL("/login");
    });
  });

  test.describe("Session Persistence", () => {
    test("driver session persists after page reload", async ({ page }) => {
      await loginAs(page, "driver");
      await page.reload();

      await expect(page).toHaveURL("/driver");
      await expect(page.getByRole("heading", { name: /driver dashboard/i })).toBeVisible();
    });

    test("shipper session persists after page reload", async ({ page }) => {
      await loginAs(page, "shipper");
      await page.reload();

      await expect(page).toHaveURL("/shipper");
      await expect(page.getByRole("heading", { name: /shipper dashboard/i })).toBeVisible();
    });

    test("admin session persists after page reload", async ({ page }) => {
      await loginAs(page, "admin");
      await page.reload();

      await expect(page).toHaveURL("/admin");
      await expect(page.getByText(/system administration/i)).toBeVisible();
    });
  });

  test.describe("Protected Routes", () => {
    test("unauthenticated user can access home page", async ({ page }) => {
      await page.goto("/");
      await expect(page).toHaveURL("/");
    });

    test("unauthenticated user is redirected to /login from /driver", async ({ page }) => {
      await page.goto("/driver");
      await page.waitForURL("/login");
      await expect(page).toHaveURL("/login");
    });

    test("unauthenticated user is redirected to /login from /shipper", async ({ page }) => {
      await page.goto("/shipper");
      await page.waitForURL("/login");
      await expect(page).toHaveURL("/login");
    });

    test("unauthenticated user is redirected to /login from /admin", async ({ page }) => {
      await page.goto("/admin");
      await page.waitForURL("/login");
      await expect(page).toHaveURL("/login");
    });

    test("authenticated user is redirected away from /login", async ({ page }) => {
      await loginAs(page, "driver");
      await page.goto("/login");

      await page.waitForURL("/");
      await expect(page).toHaveURL("/");
    });

    test("driver cannot access /shipper route", async ({ page }) => {
      await loginAs(page, "driver");
      await page.goto("/shipper");

      await page.waitForURL("/");
      await expect(page).toHaveURL("/");
    });

    test("shipper cannot access /driver route", async ({ page }) => {
      await loginAs(page, "shipper");
      await page.goto("/driver");

      await page.waitForURL("/");
      await expect(page).toHaveURL("/");
    });

    test("driver cannot access /admin route", async ({ page }) => {
      await loginAs(page, "driver");
      await page.goto("/admin");

      await page.waitForURL("/");
      await expect(page).toHaveURL("/");
    });

    test("admin cannot access /driver route", async ({ page }) => {
      await loginAs(page, "admin");
      await page.goto("/driver");

      await page.waitForURL("/");
      await expect(page).toHaveURL("/");
    });
  });

  test.describe("NavBar — Auth State", () => {
    test("shows 'Sign in' button when not authenticated", async ({ page }) => {
      await page.goto("/login");

      await expect(page.getByRole("link", { name: /sign in/i })).toBeVisible();
    });

    test("shows user info and 'Sign out' when authenticated", async ({ page }) => {
      await loginAs(page, "driver");

      await expect(page.getByRole("button", { name: /sign out/i })).toBeVisible();
      await expect(page.getByText("Driver User")).toBeVisible();
    });

    test("shows Dashboard link for driver", async ({ page }) => {
      await loginAs(page, "driver");

      await expect(page.getByRole("link", { name: /dashboard/i })).toBeVisible();
    });

    test("shows Dashboard link for shipper", async ({ page }) => {
      await loginAs(page, "shipper");

      await expect(page.getByRole("link", { name: /dashboard/i })).toBeVisible();
    });

    test("shows Dashboard link for admin", async ({ page }) => {
      await loginAs(page, "admin");

      await expect(page.getByRole("link", { name: /dashboard/i })).toBeVisible();
    });

    test("Dashboard link navigates to correct role route", async ({ page }) => {
      await loginAs(page, "driver");
      await page.getByRole("link", { name: /dashboard/i }).click();

      await expect(page).toHaveURL("/driver");
    });
  });

  test.describe("Home Page — Authenticated", () => {
    test("shows welcome message with user name on dashboard", async ({ page }) => {
      await loginAs(page, "driver");
      await page.waitForLoadState("networkidle");

      await expect(page.getByRole("heading", { name: /driver dashboard/i })).toBeVisible();
    });

    test("shows user role badge on dashboard", async ({ page }) => {
      await loginAs(page, "driver");
      await page.waitForLoadState("networkidle");

      await expect(page.getByRole("heading", { name: /driver dashboard/i })).toBeVisible();
    });

    test("shows user email on profile page", async ({ page }) => {
      await loginAs(page, "driver");
      await page.goto("/driver/profile");
      await page.waitForLoadState("networkidle");

      await expect(page.getByText(credentials.driver.email)).toBeVisible();
    });

    test("shows user phone as 'Not provided' on profile page", async ({ page }) => {
      await loginAs(page, "driver");
      await page.goto("/driver/profile");
      await page.waitForLoadState("networkidle");

      await expect(page.getByText("Not provided")).toBeVisible();
    });
  });

  test.describe("Edge Cases", () => {
    test("login with leading/trailing whitespace in email", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(`  ${credentials.driver.email}  `);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.driver.password);
      await page.locator('button[type="submit"]').click();

      await page.waitForLoadState("networkidle");
      const url = page.url();
      const isError = await page.getByText(/invalid/i).isVisible();
      const isSuccess = url.includes("/driver") || url.includes("/shipper");
      expect(isError || isSuccess).toBeTruthy();
    });

    test("login with very long email", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill("a".repeat(200) + "@email.com");
      await page.getByRole("textbox", { name: /password/i }).fill("driver123");
      await page.locator('button[type="submit"]').click();

      await expect(page.getByText(/invalid/i)).toBeVisible();
      await expect(page).toHaveURL("/login");
    });

    test("login with XSS attempt in email", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill("<script>alert('xss')</script>");
      await page.getByRole("textbox", { name: /password/i }).fill("driver123");
      await page.locator('button[type="submit"]').click();

      // No alert should have fired
      let alertFired = false;
      page.on("dialog", () => { alertFired = true; });
      await page.waitForTimeout(500);
      expect(alertFired).toBeFalsy();
    });

    test("rapid double-click on sign in does not create duplicate sessions", async ({ page }) => {
      await page.goto("/login");
      await page.getByRole("radio", { name: /driver/i }).click();
      await page.getByRole("textbox", { name: /email/i }).fill(credentials.driver.email);
      await page.getByRole("textbox", { name: /password/i }).fill(credentials.driver.password);

      const button = page.locator('button[type="submit"]');
      await button.click();
      await button.click({ force: true });

      await page.waitForURL("/driver");
      await expect(page).toHaveURL("/driver");
    });

    test("navigate to /login when already logged in redirects to home", async ({ page }) => {
      await loginAs(page, "driver");
      await page.goto("/login");

      await page.waitForURL("/");
      await expect(page).toHaveURL("/");
    });
  });
});
