import { Page } from "@playwright/test";

type Role = "driver" | "shipper" | "admin";

const credentials: Record<Role, { email: string; password: string }> = {
  admin: { email: "admin@roadlancer.com", password: "admin123" },
  driver: { email: "driver@roadlancer.com", password: "driver123" },
  shipper: { email: "shipper@roadlancer.com", password: "shipper123" },
};

export async function loginAs(page: Page, role: Role) {
  await page.goto("/login");
  await page.getByRole("radio", { name: new RegExp(role, "i") }).click();
  await page.getByRole("textbox", { name: /email/i }).fill(credentials[role].email);
  await page.getByRole("textbox", { name: /password/i }).fill(credentials[role].password);
  await page.locator('button[type="submit"]').click();
  await page.waitForURL(`/${role}`);
}

export async function logout(page: Page) {
  await page.getByRole("button", { name: /sign out/i }).click();
  await page.waitForURL("/login");
}

export { credentials };
