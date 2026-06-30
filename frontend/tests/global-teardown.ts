import { execSync } from "child_process";
import * as dotenv from "dotenv";
import { fileURLToPath } from "url";
import path from "path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, "../.env.test") });

const TEST_DB_URL =
  process.env.DATABASE_URL ||
  "postgresql://postgres:postgres@localhost:5433/roadlancer_test";

export default async function globalTeardown() {
  console.log("\n═══════════════════════════════════════");
  console.log("  Playwright Global Teardown");
  console.log("═══════════════════════════════════════\n");

  console.log("→ Truncating test database tables...");
  try {
    execSync(
      `PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d roadlancer_test -c "TRUNCATE bids, verifications, shipments, session, account, \\"user\\" CASCADE;"`,
      { stdio: "pipe" }
    );
    console.log("  ✓ Test data truncated");
  } catch (err) {
    console.error("  ✗ Truncate failed:", err);
  }

  console.log("\n  ✓ Global teardown complete\n");
}

// Allow running directly: npx tsx tests/global-teardown.ts
if (process.argv[1] && process.argv[1].endsWith("global-teardown.ts")) {
  globalTeardown()
    .then(() => process.exit(0))
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
