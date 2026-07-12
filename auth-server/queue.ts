import PgBoss from "pg-boss";
import { prisma } from "./auth.ts";

export let boss: PgBoss | null = null;

const dbUrl = process.env.DATABASE_URL || "postgresql://postgres:postgres@localhost:5432/roadlancer";

/**
 * Initializes the pg-boss queue and registers background job workers.
 */
export async function initQueue(): Promise<PgBoss | null> {
  try {
    boss = new PgBoss(dbUrl);
    boss.on("error", (error) => console.error("⚠️ [pg-boss] Queue error:", error));
    await boss.start();
    console.log("🦾 [pg-boss] Background queue started and synced with PostgreSQL");
    await boss.createQueue("classify-ticket").catch(() => {});

    await boss.work("classify-ticket", async ([job]: any) => {
      const { ticketId, subject = "", message = "" } = job ? job.data : {};
      if (!ticketId && !subject && !message) return;
      console.log(`🚀 [pg-boss worker] Processing classify-ticket job ${job?.id} for ticket: ${ticketId}`);

      try {
        const { generateText } = await import("ai");
        const { createGoogleGenerativeAI } = await import("@ai-sdk/google");
        const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_GENERATIVE_AI_API_KEY;
        if (!apiKey) {
          console.error("❌ [pg-boss worker] API key missing");
          return;
        }
        const googleProvider = createGoogleGenerativeAI({ apiKey });
        const prompt = `You are an AI classification engine for RoadLancer, an Indian logistics and transport marketplace platform.
Analyze the following support ticket subject and message, and determine the exact category and priority level.

SUBJECT: ${subject}
MESSAGE: ${message}

Choose exactly ONE category from:
- "logistics_breakdown": Vehicle breakdown, SOS, reefer temperature alarms, accident reports, checkpost detention, e-way bill mismatch.
- "billing_payment": Freight invoice delays, FASTag double deductions, fuel advances, wallet credits/debits, payment settlement.
- "verification_kyc": Driver/shipper profile review, RC book, driving license, Aadhaar, GST certificate updates, status pending.
- "shipment_tracking": GPS tracking loss, POD (Proof of Delivery) issues, return load queries, route diversion.
- "account_access": Login issues, password reset, account settings, notification preferences.
- "general": General feedback, feature inquiries, marketplace questions, referral bonuses, CSV export help.

Choose exactly ONE priority from:
- "urgent": Emergency breakdown on highway, temperature/vaccine spoilage risk, SOS alarm, active accident.
- "high": Vehicle detained at border checkpost, payment settlement blocked, verification rejected blocking urgent dispatch.
- "normal": Standard invoice inquiries, FASTag disputes, KYC review, general shipment tracking.
- "low": General platform feedback, historical reports, referral queries, notification settings.

Return strictly valid JSON with no markdown formatting or extra text:
{"category": "<category>", "priority": "<priority>", "reason": "<brief 1-sentence reason>"}`;

        let text = "";
        try {
          const res = await generateText({
            model: googleProvider("gemini-3.1-flash-lite"),
            maxTokens: 200,
            temperature: 0.2,
            maxRetries: 0,
            prompt,
          });
          text = res.text;
        } catch (firstErr) {
          const res = await generateText({
            model: googleProvider("gemini-1.5-flash"),
            maxTokens: 200,
            temperature: 0.2,
            maxRetries: 0,
            prompt,
          });
          text = res.text;
        }
        const cleanText = text.replace(/```json/g, "").replace(/```/g, "").trim();
        const parsed = JSON.parse(cleanText);
        console.log(`✨ [pg-boss worker] Classified ticket ${ticketId}:`, parsed);

        if (ticketId) {
          try {
            await prisma.support_tickets.update({
              where: { id: ticketId },
              data: {
                category: parsed.category || "general",
                priority: parsed.priority || "normal",
              },
            });
          } catch (idErr) {
            try {
              await prisma.support_tickets.update({
                where: { ticketNumber: ticketId },
                data: {
                  category: parsed.category || "general",
                  priority: parsed.priority || "normal",
                },
              });
            } catch (numErr) {
              console.warn(`⚠️ [pg-boss worker] Ticket '${ticketId}' not found in DB (diagnostic/test job). Classification completed cleanly without DB update.`);
            }
          }
        }
      } catch (err) {
        console.error("❌ [pg-boss worker] Error inside worker:", err);
        throw err;
      }
    });

    return boss;
  } catch (err) {
    console.error("⚠️ [pg-boss] Failed to initialize queue:", err);
    return null;
  }
}

/**
 * Enqueues a ticket classification job into pg-boss.
 */
export async function enqueueClassifyTicket(payload: {
  ticketId: string;
  subject: string;
  message: string;
}): Promise<string | null> {
  if (!boss) {
    console.error(`❌ [pg-boss] Queue not initialized yet. Cannot enqueue job for ticket: ${payload.ticketId}`);
    return null;
  }
  try {
    const jobId = await boss.send("classify-ticket", payload);
    if (!jobId) {
      console.error(`❌ [pg-boss] boss.send returned null. Failed to enqueue job for ticket: ${payload.ticketId}`);
    }
    return jobId;
  } catch (sendErr: any) {
    console.error(`❌ [pg-boss] Exception during job enqueue for ticket ${payload.ticketId}:`, sendErr.message || sendErr);
    return null;
  }
}
