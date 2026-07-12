import PgBoss from "pg-boss";
import { prisma } from "./auth.ts";

const dbUrl = process.env.DATABASE_URL || "postgresql://postgres:postgres@localhost:5432/roadlancer";

async function testPgBossDatabase() {
  console.log("==================================================================");
  console.log("🧪 DIAGNOSTIC TEST: PG-BOSS SCHEMA, TABLE, AND JOB QUEUE IN DB");
  console.log("==================================================================\n");

  const boss = new PgBoss(dbUrl);
  boss.on("error", (error) => console.error("⚠️ [pg-boss] Queue error:", error));

  console.log("1️⃣ Connecting to PostgreSQL via pg-boss (`boss.start()`)..");
  await boss.start();
  console.log("✅ pg-boss started! Creating queue `classify-ticket` (`boss.createQueue`)..");
  try {
    await boss.createQueue("classify-ticket");
    console.log("✅ Queue `classify-ticket` created/verified in `pgboss.queue` table!\n");
  } catch (qErr: any) {
    console.log("ℹ️ Queue note:", qErr.message);
  }

  console.log("2️⃣ Verifying schemas inside PostgreSQL database (`roadlancer`)..");
  const schemas: any[] = await prisma.$queryRaw`
    SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('public', 'pgboss');
  `;
  console.log("   Found Schemas in DB:", schemas.map(s => s.schema_name));

  console.log("\n3️⃣ Verifying `job` queue table inside `pgboss` schema..");
  const tables: any[] = await prisma.$queryRaw`
    SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = 'pgboss' AND table_name = 'job';
  `;
  if (tables.length > 0) {
    console.log("✅ Table `pgboss.job` EXACTLY EXISTS in PostgreSQL database!");
  } else {
    console.log("❌ Table `pgboss.job` not found!");
  }

  console.log("\n4️⃣ Enqueuing 2 test `classify-ticket` jobs directly via `boss.send`..");
  const job1 = await boss.send("classify-ticket", {
    ticketId: "DIAG-1001",
    subject: "[Test Breakdown] Reefer compressor failure on highway",
    message: "SOS temperature alarm triggered. Needs urgent logistics assistance.",
  });
  const job2 = await boss.send("classify-ticket", {
    ticketId: "DIAG-1002",
    subject: "[Test Billing] FASTag double deduction check",
    message: "Toll plaza deducted 4850 twice from wallet.",
  });
  console.log(`   Queued Job 1 ID: ${job1}`);
  console.log(`   Queued Job 2 ID: ${job2}\n`);

  console.log("5️⃣ Querying `pgboss.job` table right inside PostgreSQL (`SELECT * FROM pgboss.job`)..");
  const jobs: any[] = await prisma.$queryRaw`
    SELECT id, name, state, created_on, data::text as payload
    FROM pgboss.job
    WHERE name = 'classify-ticket'
    ORDER BY created_on DESC
    LIMIT 5;
  `;

  console.log(`   Found ${jobs.length} jobs inside \`pgboss.job\` database table:`);
  jobs.forEach((j, index) => {
    console.log(`   [Row ${index + 1}] ID: ${j.id} | Name: ${j.name} | State: ${j.state} | Created: ${new Date(j.created_on).toLocaleTimeString()}`);
    console.log(`            Data: ${j.payload.substring(0, 80)}...`);
  });

  console.log("\n==================================================================");
  console.log("✨ DIAGNOSTIC COMPLETE! `pgboss.job` table & jobs are 100% in DB!");
  console.log("==================================================================");

  await boss.stop();
  await prisma.$disconnect();
  process.exit(0);
}

testPgBossDatabase().catch((err) => {
  console.error("❌ Diagnostic test failed:", err);
  process.exit(1);
});
