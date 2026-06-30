import "dotenv/config";
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "./src/generated/prisma/client.ts";
import { bearer } from "better-auth/plugins";

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL!,
});

const prisma = new PrismaClient({ adapter });

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  secret: process.env.BETTER_AUTH_SECRET,
  trustedOrigins: process.env.TRUSTED_ORIGINS?.split(",") || ["http://localhost:5173"],
  emailAndPassword: {
    enabled: true,
    password: {
      minLength: 8,
    },
  },
  user: {
    additionalFields: {
      role: {
        type: ["driver", "shipper"],
        required: false,
        defaultValue: "driver",
        input: true,
      },
      phone: {
        type: "string",
        required: false,
        unique: true,
        input: true,
      },
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  rateLimit: {
    enabled: true,
    window: 60,
    max: 10,
  },
  advanced: {
    ipAddress: {
      ipAddressHeaders: ["x-forwarded-for"],
    },
  },
  plugins: [bearer()],
});
