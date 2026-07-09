import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers/auth";

// Load secret from env file (.env.test loaded by playwright.config.ts) or default
const webhookSecret = process.env.SUPPORT_WEBHOOK_SECRET || "roadlancer-webhook-secret-2026";

test.describe("Support Ticket & Inbound Email Webhook System", () => {
  test("1. API: Inbound email webhook creates ticket linked to registered user using secret", async ({ request }) => {
    const res = await request.post("http://localhost:8000/api/support/inbound-email", {
      headers: {
        "x-webhook-secret": webhookSecret,
      },
      data: {
        secret: webhookSecret,
        from_email: "driver@roadlancer.com",
        from_name: "Test Driver (Webhook)",
        subject: "[E2E API TEST] Update Registration RC",
        body: "Attached my updated RC document for verification.",
        priority: "high",
        source: "email",
      },
    });

    if (res.status() !== 200) {
      const errText = await res.text();
      console.error("\n❌ [Test 1] API Error Response (Status " + res.status() + "):", errText, "\n");
    }
    expect(res.status()).toBe(200);
    const json = await res.json();
    expect(json.success).toBe(true);
    expect(json.ticket_number).toMatch(/^TICK-\d+/);
    expect(json.ticket.sender_email).toBe("driver@roadlancer.com");
    expect(json.ticket.user).toBeDefined();
    expect(json.ticket.user.role).toBe("driver");
  });

  test("2. UI: Driver simulates inbound email in Help & Support modal and views ticket", async ({ page }) => {
    await loginAs(page, "driver");

    // Click Help & Support button in NavBar
    await page.getByRole("button", { name: /Help & Support/i }).click();
    await expect(page.getByText("RoadLancer Help & Support Desk")).toBeVisible();

    // Verify default email pre-filled with driver@roadlancer.com
    await expect(page.locator('input[placeholder="e.g. driver@roadlancer.com"]')).toHaveValue("driver@roadlancer.com");

    // Fill subject and body
    const testSubject = `UI Simulator Test ${Date.now()}`;
    await page.locator('input[placeholder*="Update DL Number"]').fill(testSubject);
    await page.locator('textarea[placeholder*="support@roadlancer.com"]').fill("Please check my new DL category details.");

    // Submit email simulation
    await page.getByRole("button", { name: /Send Email to support@roadlancer.com/i }).click();

    // Verify success banner appears with Ticket Number
    await expect(page.getByText(/Ticket Generated:/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /Copy Ticket #/i })).toBeVisible();

    // Switch to My Tickets tab and check if ticket appears
    await page.getByRole("tab", { name: /My Tickets/i }).click();
    await expect(page.getByText(testSubject)).toBeVisible();
  });

  test("3. UI: Admin reviews inbound email ticket on Admin Support Desk and resolves it", async ({ page, request }) => {
    // First generate a ticket via webhook API so we have one to inspect
    const uniqueSubject = `Admin Resolve E2E ${Date.now()}`;
    const res = await request.post("http://localhost:8000/api/support/inbound-email", {
      headers: {
        "x-webhook-secret": webhookSecret,
      },
      data: {
        secret: webhookSecret,
        from_email: "shipper@roadlancer.com",
        from_name: "Test Shipper",
        subject: uniqueSubject,
        body: "Shipper billing address update requested.",
        priority: "urgent",
        source: "email",
      },
    });
    if (res.status() !== 200) {
      const errText = await res.text();
      console.error("\n❌ [Test 3] API Error Response (Status " + res.status() + "):", errText, "\n");
    }
    expect(res.status()).toBe(200);
    const { ticket_number } = await res.json();

    // Login using shared helper as Admin
    await loginAs(page, "admin");

    // Navigate to Support Desk
    await page.goto("/admin/support");
    await expect(page.getByText("Support Desk & Inbound Emails")).toBeVisible();

    // Verify our generated ticket is present in the table
    await expect(page.getByText(ticket_number)).toBeVisible();
    await expect(page.getByText(uniqueSubject)).toBeVisible();

    // Click Inspect / Reply on the row containing our ticket
    const row = page.locator("tr", { hasText: ticket_number });
    await row.getByRole("button", { name: /Inspect \/ Reply/i }).click();

    // Verify dialog opens and displays linked RoadLancer account box
    await expect(page.getByText(/Linked RoadLancer Account:/i)).toBeVisible();
    await expect(page.locator('[role="dialog"]').getByText('shipper@roadlancer.com', { exact: true })).toBeVisible();

    // Enter Admin reply note and change status to resolved (scope to dialog to avoid hitting the filter bar dropdown)
    await page.locator('[role="dialog"] select').first().selectOption("resolved");
    await page.locator('[role="dialog"] textarea').fill("Billing address verified and profile updated by Admin.");

    // Save reply
    page.on("dialog", (dialog) => dialog.accept()); // auto-accept browser alert
    await page.getByRole("button", { name: /Save Status & Send Reply/i }).click();

    // Wait for the table to refetch after status update
    await page.waitForResponse(resp => resp.url().includes('/api/support/admin/list') && resp.status() === 200);

    // Re-locate the row after Vue re-renders the table
    const updatedRow = page.locator("tr", { hasText: ticket_number });

    // Verify status updates
    await expect(updatedRow.getByText("resolved", { exact: false })).toBeVisible();
  });
});
