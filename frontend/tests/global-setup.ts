import { execSync } from "child_process";
import * as dotenv from "dotenv";
import { fileURLToPath } from "url";
import path from "path";
import { scryptAsync } from "@noble/hashes/scrypt.js";
import { randomBytes } from "crypto";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, "../.env.test") });

const TEST_DB_URL =
  process.env.DATABASE_URL ||
  "postgresql://postgres:postgres@localhost:5433/roadlancer_test";

const DB_HOST = "localhost";
const DB_PORT = "5433";
const DB_USER = "postgres";
const DB_PASS = "postgres";
const DB_NAME = "roadlancer_test";

function psql(sql: string, database = DB_NAME) {
  const escaped = sql.replace(/"/g, '\\"');
  execSync(
    `PGPASSWORD=${DB_PASS} psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${database} -c "${escaped}"`,
    { stdio: "pipe" }
  );
}

function hexEncode(data: Uint8Array): string {
  let result = "";
  for (const byte of data) {
    result += byte.toString(16).padStart(2, "0");
  }
  return result;
}

// Match Better Auth exactly: salt is hex-encoded string passed to scryptAsync
async function hashPassword(password: string): Promise<string> {
  const saltBytes = randomBytes(16);
  const saltHex = hexEncode(new Uint8Array(saltBytes));
  // Better Auth passes the hex STRING to scryptAsync (not raw bytes)
  // scryptAsync will UTF-8 encode the hex string internally
  const key = await scryptAsync(password.normalize("NFKC"), saltHex, {
    N: 16384,
    r: 16,
    p: 1,
    dkLen: 64,
    maxmem: 128 * 16384 * 16 * 2,
  });
  return `${saltHex}:${hexEncode(new Uint8Array(key))}`;
}

async function resetDatabase() {
  console.log("→ Dropping and recreating test database...");
  try {
    psql(
      `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();`,
      "postgres"
    );
  } catch {
    // ignore if no connections
  }
  psql(`DROP DATABASE IF EXISTS ${DB_NAME}`, "postgres");
  psql(`CREATE DATABASE ${DB_NAME}`, "postgres");
  console.log("  ✓ Database reset");
}

async function runAuthMigrations() {
  console.log("→ Applying auth-server migrations...");
  const bunxBin = path.resolve(process.env.HOME || "/home/shivamsahani", ".bun/bin/bunx");
  execSync(`${bunxBin} prisma migrate deploy`, {
    cwd: path.resolve(__dirname, "../../auth-server"),
    stdio: "pipe",
    env: { ...process.env, DATABASE_URL: TEST_DB_URL },
  });
  console.log("  ✓ Auth migrations applied");
}

async function pushBackendSchema() {
  console.log("→ Generating Prisma Python client...");
  execSync("python -m prisma generate", {
    cwd: path.resolve(__dirname, "../../backend"),
    stdio: "pipe",
  });
  console.log("→ Pushing backend schema (business tables)...");
  execSync("python -m prisma db push --accept-data-loss", {
    cwd: path.resolve(__dirname, "../../backend"),
    stdio: "pipe",
    env: { ...process.env, DATABASE_URL: TEST_DB_URL },
  });
  console.log("  ✓ Backend schema pushed & client generated");
}

async function seedUsers() {
  console.log("→ Seeding test users...");

  const users = [
    { name: "Test Admin", email: "admin@roadlancer.com", password: "admin123", role: "admin" },
    { name: "Test Driver", email: "driver@roadlancer.com", password: "driver123", role: "driver" },
    { name: "Test Shipper", email: "shipper@roadlancer.com", password: "shipper123", role: "shipper" },
  ];

  for (const user of users) {
    const hashedPassword = await hashPassword(user.password);
    const id = `test_${user.role}_${Date.now()}`;

    psql(`INSERT INTO "user" (id, name, email, email_verified, role, status, created_at, updated_at)
          VALUES ('${id}', '${user.name}', '${user.email}', false, '${user.role}', 'approved', NOW(), NOW())`);

    psql(`INSERT INTO account (id, account_id, provider_id, user_id, password, created_at, updated_at)
          VALUES ('acc_${id}', '${user.email}', 'credential', '${id}', '${hashedPassword}', NOW(), NOW())`);

    console.log(`  ✓ Created ${user.email} (${user.role})`);
  }
}

export default async function globalSetup() {
  console.log("\n═══════════════════════════════════════");
  console.log("  Playwright Global Setup");
  console.log("═══════════════════════════════════════\n");

  await resetDatabase();
  await runAuthMigrations();
  await pushBackendSchema();
  await seedUsers();

  console.log("\n  ✓ Global setup complete\n");
}

// Allow running directly: bunx tsx tests/global-setup.ts
if (process.argv[1] && process.argv[1].endsWith("global-setup.ts")) {
  globalSetup()
    .then(() => process.exit(0))
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
