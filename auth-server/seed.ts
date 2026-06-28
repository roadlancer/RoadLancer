import "dotenv/config";
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "./src/generated/prisma/client.ts";

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL!,
});

const prisma = new PrismaClient({ adapter });

async function main() {
  console.log("Seeding database...");

  const users = [
    { name: "Admin User", email: "admin@roadlancer.com" },
    { name: "Driver User", email: "driver@roadlancer.com" },
    { name: "Shipper User", email: "shipper@roadlancer.com" },
  ];

  for (const userData of users) {
    const existing = await prisma.user.findUnique({
      where: { email: userData.email },
    });

    if (!existing) {
      await prisma.user.create({
        data: {
          name: userData.name,
          email: userData.email,
          emailVerified: true,
        },
      });
      console.log(`Created user: ${userData.email}`);
    } else {
      console.log(`User already exists: ${userData.email}`);
    }
  }

  console.log("Seeding complete!");
  console.log("Register passwords via the auth server API:");
  console.log("  POST http://localhost:3000/api/auth/sign-up/email");
  console.log('  Body: { "name": "...", "email": "...", "password": "..." }');
}

main()
  .catch((e) => {
    console.error("Seeding failed:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
