import "dotenv/config";
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "./src/generated/prisma/client.ts";

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL!,
});

const prisma = new PrismaClient({ adapter });

const USERS = [
  { name: "Admin User", email: "admin@roadlancer.com", password: "admin123", role: "admin" as const },
  { name: "Driver User", email: "driver@roadlancer.com", password: "driver123", role: "driver" as const },
  { name: "Shipper User", email: "shipper@roadlancer.com", password: "shipper123", role: "shipper" as const },
];

async function main() {
  console.log("Seeding database...");

  const authUrl = process.env.BETTER_AUTH_URL || "http://localhost:3000";

  for (const userData of USERS) {
    const existing = await prisma.user.findUnique({
      where: { email: userData.email },
    });

    if (existing) {
      console.log(`User already exists: ${userData.email}`);
      continue;
    }

    const res = await fetch(`${authUrl}/api/auth/sign-up/email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Origin": process.env.SEED_ORIGIN || "http://localhost:5173",
      },
      body: JSON.stringify(userData),
    });

    const data = await res.json();
    if (data.user) {
      // Approve default users so they can log in immediately
      await prisma.user.update({
        where: { email: userData.email },
        data: { status: "approved" },
      });
      console.log(`Created user: ${userData.email} (${userData.role})`);
    } else {
      console.error(`Failed to create ${userData.email}:`, data);
    }
  }

  console.log("Seeding complete!");
}

main()
  .catch((e) => {
    console.error("Seeding failed:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
