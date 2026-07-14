import { auth, prisma } from "./auth.ts";
import { initQueue, enqueueClassifyTicket, boss } from "./queue.ts";

process.on("uncaughtException", (err) => {
  console.error("❌ Uncaught exception:", err);
});
process.on("unhandledRejection", (err) => {
  console.error("❌ Unhandled rejection:", err);
});

const port = parseInt(process.env.PORT || "3000", 10);

console.log(`🔐 Better Auth server starting on http://localhost:${port}`);

initQueue();

const server = Bun.serve({
  port,
  hostname: "0.0.0.0",
  fetch: async (req: Request) => {
    const url = new URL(req.url);
    if (req.method === "POST" && (url.pathname === "/api/auth/ai/polish" || url.pathname === "/api/auth/support/polish")) {
      try {
        const body = await req.json().catch(() => ({}));
        const textToPolish = body.draft || body.message || "";
        if (!textToPolish.trim()) {
          return new Response(JSON.stringify({ error: "Draft message is required" }), {
            status: 400,
            headers: { "Content-Type": "application/json" },
          });
        }
        const { generateText } = await import("ai");
        const { createGoogleGenerativeAI } = await import("@ai-sdk/google");
        const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_GENERATIVE_AI_API_KEY;
        if (!apiKey) {
          return new Response(JSON.stringify({ error: "API key is missing on backend server", code: "API_KEY_MISSING" }), {
            status: 400,
            headers: { "Content-Type": "application/json" },
          });
        }
        const agentName = body.senderName || body.agent_name || "Sarah Jenkins (Support Lead)";
        let customerFirstName = body.customerName || body.customer_name || body.customerFirstName || "there";
        if (customerFirstName && customerFirstName !== "there") {
          customerFirstName = customerFirstName.trim().split(/\s+/)[0];
          customerFirstName = customerFirstName.charAt(0).toUpperCase() + customerFirstName.slice(1);
        } else if (body.senderEmail && typeof body.senderEmail === "string" && body.senderEmail.includes("@")) {
          const prefix = body.senderEmail.split("@")[0].replace(/[._+-].*/, "");
          if (prefix && prefix.length > 1) {
            customerFirstName = prefix.charAt(0).toUpperCase() + prefix.slice(1);
          }
        }
        const googleProvider = createGoogleGenerativeAI({ apiKey });
        const systemPrompt = `You are an AI writing assistant that polishes and improves customer support draft replies written by human agents.
Your ONLY task is to take the user's exact draft text and polish its grammar, tone, clarity, and professionalism so it sounds polite, empathetic, and well-structured.
CRITICAL RULES:
1. STRICTLY PRESERVE the exact meaning, facts, figures, dates, names, and decisions stated in the original draft.
2. DO NOT invent new facts, promises, or explanations that are not present in the original draft.
3. DO NOT write a completely different or generic customer service response. You must improve and rewrite the exact draft provided.
4. Output ONLY the final polished reply text directly, without any introductory words, notes, quotes, or markdown formatting around it.
5. SIGNATURE REQUIREMENT: Always conclude the polished reply with a clean, professional signature block in the exact following format at the bottom:

Best regards,
${agentName}
RoadLancer Support Team
https://roadlancer.com

(If the original draft already contained an informal sign-off or name, replace it with this standardized signature block.)
6. GREETING REQUIREMENT: Always begin the polished reply by addressing the customer respectfully by their first name "${customerFirstName}" at the very top (for example: "Hi ${customerFirstName}," or "Dear ${customerFirstName},"). If the original draft already had a greeting with a different name or no name at all, update or prepend it so it starts cleanly by addressing "${customerFirstName}".`;
        const promptText = `Please polish and improve the following support agent draft reply while preserving its exact facts and meaning:\n\n---\n${textToPolish.trim()}\n---`;
        
        let text = "";
        let usage: any = null;
        try {
          const res = await generateText({
            model: googleProvider("gemini-3.1-flash-lite"),
            maxTokens: 350,
            temperature: 0.3,
            maxRetries: 0,
            system: systemPrompt,
            prompt: promptText,
          });
          text = res.text;
          usage = res.usage;
        } catch (firstErr: any) {
          const firstMsg = (firstErr?.message || "").toLowerCase();
          if (firstMsg.includes("quota") || firstMsg.includes("rate") || firstMsg.includes("429") || firstErr?.status === 429 || firstMsg.includes("not found") || firstMsg.includes("404") || firstErr?.status === 404 || firstMsg.includes("is not supported") || firstMsg.includes("invalid model")) {
            const fallbackRes = await generateText({
              model: googleProvider("gemini-2.5-flash"),
              maxTokens: 350,
              temperature: 0.3,
              maxRetries: 0,
              system: systemPrompt,
              prompt: promptText,
            });
            text = fallbackRes.text;
            usage = fallbackRes.usage;
          } else {
            throw firstErr;
          }
        }

        let finalPolished = text.trim();
        if (customerFirstName && customerFirstName !== "there") {
          const topSlice = finalPolished.slice(0, 80).toLowerCase();
          if (!topSlice.includes(customerFirstName.toLowerCase())) {
            finalPolished = `Hi ${customerFirstName},\n\n${finalPolished}`;
          }
        }
        if (!finalPolished.includes("https://roadlancer.com")) {
          finalPolished += `\n\nBest regards,\n${agentName}\nRoadLancer Support Team\nhttps://roadlancer.com`;
        }

        return new Response(JSON.stringify({ 
          polished: finalPolished, 
          success: true,
          usage: usage || { promptTokens: 0, completionTokens: 0, totalTokens: 0 },
          source: "Backend Server"
        }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      } catch (err: any) {
        console.error("Error polishing reply in auth-server:", err);
        const errMsg = err?.message || "Failed to polish reply";
        const errMsgUpper = errMsg.toUpperCase();
        let code = "UNKNOWN_ERROR";
        let status = 500;
        if (errMsgUpper.includes("API_KEY_INVALID") || errMsgUpper.includes("KEY NOT VALID") || errMsgUpper.includes("401") || errMsgUpper.includes("UNAUTHORIZED") || err?.status === 401 || err?.status === 403) {
          code = "API_KEY_INVALID";
          status = 401;
        } else if (errMsgUpper.includes("QUOTA") || errMsgUpper.includes("RATE") || errMsgUpper.includes("RESOURCE_EXHAUSTED") || errMsgUpper.includes("429") || err?.status === 429) {
          code = "TOKEN_QUOTA_EXHAUSTED";
          status = 429;
        }
        return new Response(JSON.stringify({ error: errMsg, code }), {
          status,
          headers: { "Content-Type": "application/json" },
        });
      }
    }

    if (req.method === "POST" && url.pathname === "/api/auth/ai/summarize") {
      try {
        const body = await req.json();
        const { generateText } = await import("ai");
        const { createGoogleGenerativeAI } = await import("@ai-sdk/google");
        const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_GENERATIVE_AI_API_KEY;
        if (!apiKey) {
          return new Response(JSON.stringify({ error: "API key is missing on backend server", code: "API_KEY_MISSING" }), {
            status: 400,
            headers: { "Content-Type": "application/json" },
          });
        }
        const googleProvider = createGoogleGenerativeAI({ apiKey });
        const replies = Array.isArray(body.replies) ? body.replies : [];
        const repliesText = replies
          .map((r: any) => `[${(r.sender_role || "user").toUpperCase()} - ${r.sender_name || "User"}]: ${r.message}`)
          .join("\n\n");
        const promptInput = `TICKET SUBJECT: ${body.subject || "N/A"}\n\nORIGINAL CUSTOMER MESSAGE:\n${body.message || "N/A"}\n\nCONVERSATION HISTORY (${replies.length} replies):\n${repliesText || "No replies yet."}`;
        
        const systemPrompt = `You are an AI support assistant for RoadLancer (a trucking and logistics platform).
Your task is to provide a concise, high-level summary of the support ticket and any subsequent conversation/replies.
Structure your summary cleanly with:
1. **Issue Overview**: A 1-2 sentence summary of the customer's core issue or request.
2. **Current Status & Key Updates**: What has been discussed or resolved in the replies so far (if any).
3. **Next Action Required**: What should the support agent do next to resolve or move this ticket forward.
Output ONLY the markdown summary directly without extra chatter or intro text.`;

        let text = "";
        let usage: any = null;
        try {
          const res = await generateText({
            model: googleProvider("gemini-3.1-flash-lite"),
            maxTokens: 400,
            temperature: 0.3,
            maxRetries: 0,
            system: systemPrompt,
            prompt: promptInput,
          });
          text = res.text;
          usage = res.usage;
        } catch (firstErr: any) {
          const firstMsg = (firstErr?.message || "").toLowerCase();
          if (firstMsg.includes("quota") || firstMsg.includes("rate") || firstMsg.includes("429") || firstErr?.status === 429 || firstMsg.includes("not found") || firstMsg.includes("404") || firstErr?.status === 404 || firstMsg.includes("is not supported") || firstMsg.includes("invalid model")) {
            const fallbackRes = await generateText({
              model: googleProvider("gemini-2.5-flash"),
              maxTokens: 400,
              temperature: 0.3,
              maxRetries: 0,
              system: systemPrompt,
              prompt: promptInput,
            });
            text = fallbackRes.text;
            usage = fallbackRes.usage;
          } else {
            throw firstErr;
          }
        }

        return new Response(JSON.stringify({ 
          summary: text.trim(), 
          success: true,
          usage: usage || { promptTokens: 0, completionTokens: 0, totalTokens: 0 },
          source: "Backend Server"
        }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      } catch (err: any) {
        console.error("Error summarizing ticket in auth-server:", err);
        const errMsg = err?.message || "Failed to summarize ticket";
        const errMsgUpper = errMsg.toUpperCase();
        let code = "UNKNOWN_ERROR";
        let status = 500;
        if (errMsgUpper.includes("API_KEY_INVALID") || errMsgUpper.includes("KEY NOT VALID") || errMsgUpper.includes("401") || errMsgUpper.includes("UNAUTHORIZED") || err?.status === 401 || err?.status === 403) {
          code = "API_KEY_INVALID";
          status = 401;
        } else if (errMsgUpper.includes("QUOTA") || errMsgUpper.includes("RATE") || errMsgUpper.includes("RESOURCE_EXHAUSTED") || errMsgUpper.includes("429") || err?.status === 429) {
          code = "TOKEN_QUOTA_EXHAUSTED";
          status = 429;
        }
        return new Response(JSON.stringify({ error: errMsg, code }), {
          status,
          headers: { "Content-Type": "application/json" },
        });
      }
    }

    if (req.method === "POST" && url.pathname === "/api/auth/ai/classify") {
      try {
        const body = await req.json().catch(() => ({}));
        const { ticketId = "", subject = "", message = "", senderName = "", background = false } = body;
        if (!subject.trim() && !message.trim() && !ticketId) {
          return new Response(JSON.stringify({ error: "ticketId, subject, or message is required" }), {
            status: 400,
            headers: { "Content-Type": "application/json" },
          });
        }

        if (background || ticketId) {
          const jobId = await enqueueClassifyTicket({ ticketId, subject, message, senderName });
          if (jobId) {
            console.log(`📦 [pg-boss] Queued classify-ticket job ${jobId} for ticket: ${ticketId}`);
            return new Response(JSON.stringify({ success: true, jobId, message: "Classification job queued via pg-boss" }), {
              status: 202,
              headers: { "Content-Type": "application/json" },
            });
          } else {
            console.warn("⚠️ [pg-boss] Boss queue not initialized or job failed, running local async execution");
          }
        }

        const { generateText } = await import("ai");
        const { createGoogleGenerativeAI } = await import("@ai-sdk/google");
        const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_GENERATIVE_AI_API_KEY;
        if (!apiKey) {
          return new Response(JSON.stringify({ error: "API key is missing on backend server", code: "API_KEY_MISSING" }), {
            status: 400,
            headers: { "Content-Type": "application/json" },
          });
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
            model: googleProvider("gemini-2.5-flash"),
            maxTokens: 200,
            temperature: 0.2,
            maxRetries: 0,
            prompt,
          });
          text = res.text;
        } catch (firstErr: any) {
          const res = await generateText({
            model: googleProvider("gemini-3-flash"),
            maxTokens: 200,
            temperature: 0.2,
            maxRetries: 0,
            prompt,
          });
          text = res.text;
        }
        const cleanText = text.replace(/```json/g, "").replace(/```/g, "").trim();
        const parsed = JSON.parse(cleanText);
        console.log("✨ [auth-server/classify] Classified ticket:", parsed);

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
              `INSERT INTO ticket_replies (id, ticket_id, sender_name, sender_role, sender_type, message, created_at, updated_at)
               VALUES ($1, $2, 'RoadLancer AI Agent', 'admin', 'agent', $3, NOW(), NOW())`,
              replyId,
              ticketId,
              parsed.resolutionReply
            );
            console.log(`🤖 [auth-server/classify] Auto-resolved ticket ${ticketId} with automated reply!`);
            
            // Send email notification for auto-resolved ticket
            try {
              const ticketRows = await prisma.$queryRawUnsafe<any[]>(
                `SELECT id, ticket_number, sender_email, sender_name, subject 
                 FROM support_tickets WHERE id = $1 OR ticket_number = $1 LIMIT 1`,
                ticketId
              );
              const ticket = ticketRows?.[0];
              if (ticket?.sender_email) {
                const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
                const webhookSecret = process.env.SUPPORT_WEBHOOK_SECRET || 'roadlancer-webhook-secret-2026';
                await fetch(`${backendUrl}/api/support/notify-email`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'x-webhook-secret': webhookSecret,
                  },
                  body: JSON.stringify({
                    ticketId: ticket.id,
                    ticketNumber: ticket.ticket_number,
                    recipientEmail: ticket.sender_email,
                    recipientName: ticket.sender_name || '',
                    subject: ticket.subject || '',
                    replyMessage: parsed.resolutionReply,
                  }),
                });
                console.log(`📧 [auth-server/classify] Email notification sent for ticket ${ticketId}`);
              }
            } catch (emailErr: any) {
              console.error(`⚠️ [auth-server/classify] Failed to send email notification:`, emailErr?.message || emailErr);
            }
          }
        }

        return new Response(JSON.stringify({ success: true, classification: parsed }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err?.message || "Failed to classify ticket" }), {
          status: 500,
          headers: { "Content-Type": "application/json" },
        });
      }
    }

    const origin = req.headers.get("origin") || "";
    const allowedOrigins = (process.env.TRUSTED_ORIGINS || "").split(",").map((s: string) => s.trim());

    if (req.method === "OPTIONS") {
      const isAllowed = allowedOrigins.some((o: string) => origin === o) || origin.includes("localhost");
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": isAllowed ? origin : allowedOrigins[0] || "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-Id",
          "Access-Control-Allow-Credentials": "true",
          "Access-Control-Max-Age": "86400",
        },
      });
    }

    const corsHeaders: Record<string, string> = {};
    if (origin) {
      const isAllowed = allowedOrigins.some((o: string) => origin === o) || origin.includes("localhost");
      if (isAllowed) {
        corsHeaders["Access-Control-Allow-Origin"] = origin;
        corsHeaders["Access-Control-Allow-Credentials"] = "true";
      }
    }

    try {
      const res = await auth.handler(req);
      Object.entries(corsHeaders).forEach(([k, v]) => res.headers.set(k, v));
      if (res.status >= 400) {
        const errBody = await res.clone().text().catch(() => "");
        console.error(`❌ [auth] ${res.status} ${url.pathname}: ${errBody.substring(0, 300)}`);
      }
      return res;
    } catch (err: any) {
      console.error(`❌ [auth] THREW ${url.pathname}:`, err?.message || err);
      return new Response(JSON.stringify({ error: err?.message }), { status: 500, headers: { "Content-Type": "application/json" } });
    }
  },
});

console.log(`✅ Better Auth server running on http://localhost:${port}`);
console.log(`📋 Health check: http://localhost:${port}/api/auth/ok`);
console.log(`🔗 Auth API: http://localhost:${port}/api/auth/`);
