-- CreateEnum
CREATE TYPE "Role" AS ENUM ('driver', 'shipper', 'admin');

-- AlterTable
ALTER TABLE "user" ADD COLUMN "suspended" BOOLEAN NOT NULL DEFAULT false;

-- AlterColumn (convert TEXT to enum)
ALTER TABLE "user" ALTER COLUMN "role" DROP DEFAULT;
UPDATE "user" SET "role" = 'driver' WHERE "role" NOT IN ('driver', 'shipper', 'admin');
ALTER TABLE "user" ALTER COLUMN "role" TYPE "Role" USING "role"::"Role";
ALTER TABLE "user" ALTER COLUMN "role" SET DEFAULT 'driver';
