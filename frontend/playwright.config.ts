import { defineConfig, devices } from "@playwright/test";
import * as dotenv from "dotenv";
import { fileURLToPath } from "url";
import path from "path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, ".env.test") });

export default defineConfig({
  testDir: "./tests",
  outputDir: "./tests/test-results",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["html", { open: "never" }]],

  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "on-first-retry",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"], channel: "chrome" },
    },
  ],

  webServer: [
    {
      command: "cd ../auth-server && node --require tsx/cjs server.ts",
      port: 3000,
      reuseExistingServer: !process.env.CI,
      cwd: "../auth-server",
      env: {
        DATABASE_URL: "postgresql://postgres:postgres@localhost:5433/roadlancer_test",
        BETTER_AUTH_URL: "http://localhost:3000",
        BETTER_AUTH_SECRET: "test-secret-key-for-e2e-only",
        TRUSTED_ORIGINS: "http://localhost:5173",
      },
      timeout: 15000,
    },
    {
      command: "cd ../backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000",
      port: 8000,
      reuseExistingServer: !process.env.CI,
      cwd: "../backend",
      env: {
        DATABASE_URL: "postgresql://postgres:postgres@localhost:5433/roadlancer_test",
      },
      timeout: 15000,
    },
    {
      command: "npx vite --port 5173",
      port: 5173,
      reuseExistingServer: !process.env.CI,
      timeout: 15000,
    },
  ],

  globalSetup: "./tests/global-setup.ts",
  globalTeardown: "./tests/global-teardown.ts",
});
