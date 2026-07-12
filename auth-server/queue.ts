import PgBoss from "pg-boss";
import fs from "fs/promises";
import path from "path";
import dotenv from "dotenv";
dotenv.config({ path: path.resolve(__dirname, "../.env") });
dotenv.config();
import { prisma } from "./auth.ts";

export let boss: PgBoss | null = null;

const dbUrl = process.env.DATABASE_URL || "postgresql://postgres:postgres@localhost:5432/roadlancer";

let cachedModelName: string | null = null;
async function getBestAvailableModel(apiKey: string): Promise<string> {
  if (cachedModelName) return cachedModelName;
  try {
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`, {
      signal: AbortSignal.timeout(2000)
    });
    if (res.ok) {
      const data = await res.json();
      const models: any[] = data.models || [];
      const supported = models.filter((m: any) =>
        (m.supportedGenerationMethods || []).includes("generateContent") &&
        !m.name.includes("tts") &&
        !m.name.includes("image") &&
        !m.name.includes("preview")
      );
      const flashModel = supported.find((m: any) => m.name.includes("2.5-flash") || m.name.includes("3-flash"));
      const anyModel = supported[0];
      const selected = flashModel || anyModel;
      if (selected && selected.name) {
        cachedModelName = selected.name.replace(/^models\//, "");
        console.log(`🧠 [pg-boss worker] Auto-discovered valid Gemini model for your API key: ${cachedModelName}`);
        return cachedModelName;
      }
    }
  } catch (err) {
    console.warn("⚠️ [pg-boss worker] Could not query ListModels API quickly, using gemini-2.5-flash");
  }
  cachedModelName = "gemini-2.5-flash";
  return cachedModelName;
}

/**
 * Initializes the pg-boss queue and registers background job workers.
 */
export async function initQueue(): Promise<PgBoss | null> {
  try {
    boss = new PgBoss({ connectionString: dbUrl, newPollInterval: 500 });
    boss.on("error", (error) => console.error("⚠️ [pg-boss] Queue error:", error));
    await boss.start();
    console.log("🦾 [pg-boss] Background queue started (fast poll 500ms) and synced with PostgreSQL");
    const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_GENERATIVE_AI_API_KEY;
    if (apiKey) getBestAvailableModel(apiKey).catch(() => {});
    await boss.createQueue("classify-ticket").catch(() => {});

    await boss.work("classify-ticket", async (jobOrJobs: any) => {
      const job = Array.isArray(jobOrJobs) ? jobOrJobs[0] : jobOrJobs;
      const { ticketId, subject = "", message = "", senderName = "" } = job ? (job.data || {}) : {};
      if (!ticketId && !subject && !message) return;
      console.log(`🚀 [pg-boss worker] Processing classify-ticket job ${job?.id} for ticket: ${ticketId}`);

      try {
        if (ticketId) {
          await prisma.$executeRawUnsafe(`UPDATE support_tickets SET status = 'processing' WHERE id = $1 OR ticket_number = $1`, ticketId).catch(() => {});
        }

        const { generateText } = await import("ai");
        const { createGoogleGenerativeAI } = await import("@ai-sdk/google");
        const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_GENERATIVE_AI_API_KEY;
        if (!apiKey) {
          console.error("❌ [pg-boss worker] API key missing");
          if (ticketId) {
            await prisma.$executeRawUnsafe(`UPDATE support_tickets SET status = 'open' WHERE id = $1 OR ticket_number = $1`, ticketId).catch(() => {});
          }
          return { status: "error", error: "GEMINI_API_KEY missing" };
        }
        const googleProvider = createGoogleGenerativeAI({ apiKey });
        const kbText = await fs.readFile(path.resolve(__dirname, "../knowledge-base.md"), "utf-8").catch(() => "");

        // Extract first name from senderName (e.g. "Rajesh Kumar" -> "Rajesh")
        const firstName = (senderName || "").split(/\s+/).filter(Boolean)[0] || "there";

        const prompt = `You are an AI classification and auto-resolution engine for RoadLancer, an Indian logistics and transport marketplace platform.
Analyze the following support ticket subject and message against our Knowledge Base to classify the ticket AND determine if it can be auto-resolved immediately.

CUSTOMER NAME: ${senderName || "Customer"}
CUSTOMER FIRST NAME: ${firstName}
SUBJECT: ${subject}
MESSAGE: ${message}

KNOWLEDGE BASE:
${kbText}

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

Auto-Resolution Rules:
1. If the ticket is an emergency/SOS (priority "urgent" or "high", breakdowns, checkpost detention, or complex disputes requiring human investigation), set "canAutoResolve": false and "resolutionReply": "".
2. If the ticket is a standard FAQ / inquiry covered directly by the Knowledge Base (e.g., FASTag double deduction refund timeline, KYC approval 2-4 hours, freight invoice 24-48 hours, fuel advance 70%, POD upload instructions, password reset / WhatsApp OTP, CSV export), set "canAutoResolve": true and write a reply using the guidelines below.

Reply Formatting Rules (when canAutoResolve is true):
- Address the customer by their FIRST NAME (e.g. "Dear Rajesh,")
- Use a warm, professional, customer-friendly tone throughout
- Format the reply as clean HTML (use <p>, <strong>, <ul>, <li>, <br> tags)
- Structure: greeting → acknowledge their issue → provide the solution/answer → offer further help → sign off
- End with: <br><br>Best regards,<br><strong>RoadLancer Support Team</strong>
- Do NOT include markdown backticks or code fences in the reply text
- Keep the reply concise but helpful — 3 to 6 short paragraphs maximum

Return strictly valid JSON with no markdown formatting or extra text:
{"category": "<category>", "priority": "<priority>", "reason": "<brief 1-sentence reason>", "canAutoResolve": <true/false>, "resolutionReply": "<HTML reply text or empty text>"}`;

        const bestModel = await getBestAvailableModel(apiKey);
        let text = "";
        try {
          const res = await generateText({
            model: googleProvider(bestModel),
            maxTokens: 8192,
            temperature: 0.2,
            maxRetries: 1,
            prompt,
          });
          text = res.text;
        } catch (firstErr) {
          console.warn(`⚠️ [pg-boss worker] Primary model ${bestModel} failed, retrying with gemini-2.5-flash:`, (firstErr as any)?.message);
          const res = await generateText({
            model: googleProvider("gemini-2.5-flash"),
            maxTokens: 8192,
            temperature: 0.2,
            maxRetries: 1,
            prompt,
          });
          text = res.text;
        }
        const cleanText = text.replace(/```json/g, "").replace(/```/g, "").trim();
        const jsonMatch = cleanText.match(/\{[\s\S]*\}/);
        let parsed: any;
        try {
          parsed = JSON.parse(jsonMatch ? jsonMatch[0] : cleanText);
        } catch (parseErr) {
          console.error("❌ [pg-boss worker] JSON parse failed. Raw text:", text.substring(0, 500));
          console.error("❌ [pg-boss worker] Cleaned text:", cleanText.substring(0, 500));
          throw parseErr;
        }
        console.log(`✨ [pg-boss worker] Classified & Auto-Resolve checked ticket ${ticketId}:`, parsed);

        if (ticketId) {
          const isAutoResolved = Boolean(parsed.canAutoResolve && parsed.resolutionReply && parsed.resolutionReply.trim());
          const newStatus = isAutoResolved ? "resolved" : "open";
          const notePrefix = isAutoResolved
            ? `[AI_AUTO_RESOLVED] Automatically resolved upon arrival using RoadLancer knowledge base. Reason: ${parsed.reason || ""}`
            : `[AI_CLASSIFIED] Auto-classified via Gemini. Reason: ${parsed.reason || ""}`;

          await prisma.$executeRawUnsafe(
            `UPDATE support_tickets SET category = $1, priority = $2, status = $3, admin_notes = $4 WHERE id = $5 OR ticket_number = $5`,
            parsed.category || "general",
            parsed.priority || "normal",
            newStatus,
            notePrefix,
            ticketId
          );
          if (isAutoResolved) {
            const replyId = crypto.randomUUID();
            await prisma.$executeRawUnsafe(
`INSERT INTO ticket_replies (id, ticket_id, sender_name, sender_role, sender_type, message, created_at)
                 VALUES ($1, $2, 'RoadLancer AI Agent', 'admin', 'agent', $3, NOW())`,
              replyId,
              ticketId,
              parsed.resolutionReply
            );
            console.log(`🤖 [pg-boss worker] Auto-resolved ticket ${ticketId} with automated reply!`);
          }
        }
        return parsed;
      } catch (err: any) {
        console.error("❌ [pg-boss worker] Error inside worker:", err?.message || err);
        if (ticketId) {
          await prisma.$executeRawUnsafe(`UPDATE support_tickets SET status = 'open' WHERE id = $1 OR ticket_number = $1`, ticketId).catch(() => {});
        }
        return { status: "error", error: err?.message || String(err) };
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
  senderName?: string;
}): Promise<string | null> {
  if (!boss) {
    console.log(`⚠️ [pg-boss] Queue not initialized or dropped. Attempting initQueue for ticket: ${payload.ticketId}...`);
    await initQueue();
  }
  if (!boss) {
    console.error(`❌ [pg-boss] Queue failed to initialize. Cannot enqueue job for ticket: ${payload.ticketId}`);
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
