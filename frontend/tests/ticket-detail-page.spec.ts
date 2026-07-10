import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers/auth";

const webhookSecret = process.env.SUPPORT_WEBHOOK_SECRET || "roadlancer-webhook-secret-2026";

test.describe("Admin Ticket Details Page (/admin/support/:id) Full-Stack E2E Integration", () => {
  let createdTicketId: string;
  let createdTicketNumber: string;
  const uniqueSubject = `E2E Full-Stack Test: Engine Telemetry ${Date.now()}`;
  const uniqueBody = "Real-time diagnostic alert triggered on shipment route #808.";

  test.beforeAll(async ({ request }) => {
    // Generate a real ticket in the test database via backend API
    const res = await request.post("http://localhost:8000/api/support/inbound-email", {
      headers: {
        "x-webhook-secret": webhookSecret,
      },
      data: {
        secret: webhookSecret,
        from_email: "driver@roadlancer.com",
        from_name: "Test Driver (E2E)",
        subject: uniqueSubject,
        body: uniqueBody,
        priority: "urgent",
        source: "email",
      },
    });

    expect(res.status()).toBe(200);
    const json = await res.json();
    expect(json.success).toBe(true);
    createdTicketId = json.ticket.id;
    createdTicketNumber = json.ticket_number;
  });

  test("1. Full-Stack Navigation & Fetching: Admin inspects ticket from Support Desk and loads real backend data on standalone route", async ({ page }) => {
    await loginAs(page, "admin");

    // Navigate to Support Desk table
    await page.goto("/admin/support");
    await expect(page.getByText("Support Desk & Inbound Emails")).toBeVisible();

    // Locate the row in the table and click Inspect
    const ticketRow = page.locator("tr", { hasText: createdTicketNumber });
    await expect(ticketRow).toBeVisible();
    await ticketRow.getByRole("button", { name: /Inspect/i }).click();

    // Verify Vue Router navigation to /admin/support/:id and full-stack data hydration from FastAPI
    await page.waitForURL(new RegExp(`/admin/support/${createdTicketId}`));
    await expect(page.getByText(`#${createdTicketNumber}`)).toBeVisible();
    await expect(page.getByTestId("ticket-subject-title")).toHaveText(uniqueSubject);
  });

  test("2. Full-Stack Persistence across views: Admin saves resolution status & submits reply, then verifies persistence across route transitions", async ({ page }) => {
    await loginAs(page, "admin");
    await page.goto(`/admin/support/${createdTicketId}`);
    await expect(page.getByText(`#${createdTicketNumber}`)).toBeVisible();

    // Auto-accept confirmation alerts from API responses
    page.on("dialog", (dialog) => dialog.accept());

    // 1. Submit a real reply via ReplyForm and verify backend persistence in ReplyThread
    const replyText = `Dispatched technical crew at ${Date.now()}.`;
    await page.getByTestId("reply-message-textarea").fill(replyText);
    await page.getByTestId("reply-submit-button").click();

    const repliesList = page.getByTestId("replies-list");
    await expect(repliesList).toBeVisible();
    await expect(repliesList).toContainText(replyText);

    // 2. Update status and save via Resolution Desk
    await page.getByTestId("status-select").selectOption("in_progress");
    await page.getByTestId("save-resolution-btn").click();

    // Verify status update is reflected on standalone page
    await expect(page.getByTestId("status-select")).toHaveValue("in_progress");

    // 3. Navigate back to main Support Desk table and verify backend persistence across routes
    await page.getByRole("button", { name: /Back to Support Desk/i }).click();
    await page.waitForURL("/admin/support");

    const updatedRow = page.locator("tr", { hasText: createdTicketNumber });
    await expect(updatedRow).toBeVisible();
    await expect(updatedRow.locator('select[aria-label="Change status"]')).toHaveValue("in_progress");
  });
});
