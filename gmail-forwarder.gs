// =====================================================
// Gmail → RoadLancer Auto-Forwarder
// =====================================================
// Deploy this as a Google Apps Script to auto-forward
// emails from support.roadlancer@gmail.com to the
// RoadLancer support ticket API.
//
// SETUP INSTRUCTIONS:
// 1. Go to https://script.google.com
// 2. Create new project, paste this code
// 3. Update WEBHOOK_URL below
// 4. Run setup() function first (authorizes Gmail access)
// 5. Run startForwarder() to begin auto-forwarding
// 6. (Optional) Set time-driven trigger for every 1-5 min
// =====================================================

const WEBHOOK_URL = "https://backend-production-1f57.up.railway.app/api/support/inbound-email";
const WEBHOOK_SECRET = "roadlancer-webhook-secret-2026";
const LABEL_NAME = "RoadLancer-Processed";

// =====================================================
// MAIN: Process unread emails
// =====================================================
function forwardEmails() {
  const label = getOrCreateLabel(LABEL_NAME);
  const threads = GmailApp.search("in:inbox is:unread -label:" + LABEL_NAME, 0, 10);

  if (threads.length === 0) {
    Logger.log("No new emails to process");
    return;
  }

  Logger.log("Found " + threads.length + " new email(s) to process");

  for (let i = 0; i < threads.length; i++) {
    const thread = threads[i];
    const messages = thread.getMessages();

    // Process the latest message in the thread
    const msg = messages[messages.length - 1];
    try {
      processMessage(msg, label);
    } catch (e) {
      Logger.log("Error processing message: " + e.toString());
    }

    // Small delay between emails
    Utilities.sleep(1000);
  }
}

// =====================================================
// PROCESS: Extract email data and send to webhook
// =====================================================
function processMessage(msg, label) {
  const from = msg.getFrom();
  const fromEmail = extractEmail(from);
  const fromName = extractName(from);
  const subject = msg.getSubject();
  const body = getPlainTextBody(msg);
  const date = msg.getDate();
  const threadId = msg.getThread().getId();
  const messageId = msg.getHeader("Message-ID") || "";

  // Skip emails from ourselves (sent by RoadLancer)
  if (fromEmail === "support.roadlancer@gmail.com") {
    Logger.log("Skipping self-sent email: " + subject);
    label.addToThread(msg.getThread());
    return;
  }

  // Skip automated/bounce emails
  if (isAutoReply(msg)) {
    Logger.log("Skipping auto-reply: " + subject);
    label.addToThread(msg.getThread());
    return;
  }

  // Determine category from subject/body
  const category = categorizeEmail(subject, body);

  // Build webhook payload
  const payload = {
    from_email: fromEmail,
    from_name: fromName,
    subject: subject,
    body: body,
    category: category,
    priority: detectPriority(subject, body),
    source: "email",
    received_at: date.toISOString(),
    gmail_thread_id: threadId,
    gmail_message_id: messageId
  };

  Logger.log("Forwarding email from " + fromEmail + ": " + subject);

  // Send to webhook
  const options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "x-webhook-secret": WEBHOOK_SECRET
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(WEBHOOK_URL, options);
    const responseCode = response.getResponseCode();
    const responseBody = response.getContentText();

    if (responseCode === 200) {
      Logger.log("✅ Email forwarded successfully: " + subject);
      label.addToThread(msg.getThread());
    } else {
      Logger.log("❌ Webhook error (" + responseCode + "): " + responseBody);
    }
  } catch (e) {
    Logger.log("❌ Failed to send webhook: " + e.toString());
  }
}

// =====================================================
// HELPERS
// =====================================================

function extractEmail(from) {
  const match = from.match(/<(.+?)>/);
  return match ? match[1] : from;
}

function extractName(from) {
  const match = from.match(/^"?([^"<]+)"?\s*</);
  return match ? match[1].trim() : extractEmail(from);
}

function getPlainTextBody(msg) {
  let body = msg.getPlainBody();
  if (!body) {
    body = msg.getBody().replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
  }
  // Limit body length
  if (body.length > 2000) {
    body = body.substring(0, 2000) + "...";
  }
  return body;
}

function isAutoReply(msg) {
  const subject = msg.getSubject().toLowerCase();
  const autoHeaders = [
    "auto-reply", "automatic reply", "out of office",
    "undelivered", "delivery failure", "mail delivery",
    "return mail", "bounce", "noreply", "no-reply"
  ];
  return autoHeaders.some(h => subject.includes(h));
}

function categorizeEmail(subject, body) {
  const text = (subject + " " + body).toLowerCase();

  if (text.includes("fastag") || text.includes("toll") || text.includes("tag"))
    return "fastag";
  if (text.includes("kyc") || text.includes("verification") || text.includes("document"))
    return "kyc";
  if (text.includes("gps") || text.includes("tracking") || text.includes("location"))
    return "gps";
  if (text.includes("pod") || text.includes("proof of delivery") || text.includes("delivery proof"))
    return "pod";
  if (text.includes("otp") || text.includes("password") || text.includes("login") || text.includes("access"))
    return "account_access";
  if (text.includes("payment") || text.includes("refund") || text.includes("charge") || text.includes("billing"))
    return "payment";
  if (text.includes("shipment") || text.includes("booking") || text.includes("pickup") || text.includes("delivery"))
    return "shipment";
  if (text.includes("complaint") || text.includes("issue") || text.includes("problem"))
    return "complaint";

  return "general";
}

function detectPriority(subject, body) {
  const text = (subject + " " + body).toLowerCase();
  if (text.includes("urgent") || text.includes("emergency") || text.includes("immediately"))
    return "urgent";
  if (text.includes("important") || text.includes("critical"))
    return "high";
  return "normal";
}

function getOrCreateLabel(name) {
  const labels = GmailApp.getUserLabels();
  for (let i = 0; i < labels.length; i++) {
    if (labels[i].getName() === name) {
      return labels[i];
    }
  }
  return GmailApp.createLabel(name);
}

// =====================================================
// SETUP FUNCTIONS (Run these once)
// =====================================================

function setup() {
  Logger.log("=== RoadLancer Gmail Forwarder Setup ===");
  Logger.log("Testing Gmail access...");

  // Test Gmail access
  const label = getOrCreateLabel(LABEL_NAME);
  Logger.log("✅ Gmail label created/found: " + LABEL_NAME);

  // Test webhook
  Logger.log("Testing webhook connection...");
  const testPayload = {
    from_email: "setup-test@roadlancer.com",
    from_name: "Setup Test",
    subject: "Setup test - ignore",
    body: "This is a setup test email",
    category: "general",
    priority: "normal",
    source: "setup_test"
  };

  try {
    const response = UrlFetchApp.fetch(WEBHOOK_URL, {
      method: "post",
      contentType: "application/json",
      headers: { "x-webhook-secret": WEBHOOK_SECRET },
      payload: JSON.stringify(testPayload),
      muteHttpExceptions: true
    });
    Logger.log("✅ Webhook test: " + response.getResponseCode());
  } catch (e) {
    Logger.log("❌ Webhook test failed: " + e.toString());
  }

  Logger.log("=== Setup complete! ===");
  Logger.log("Run startForwarder() to begin forwarding emails");
}

function startForwarder() {
  Logger.log("Starting email forwarder...");
  forwardEmails();
  Logger.log("Done! Check logs for details.");
}

// =====================================================
// TRIGGER: Set up auto-forwarding (run once)
// =====================================================
function createTimeTrigger() {
  // Remove existing triggers first
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "forwardEmails") {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }

  // Create new trigger: run every 2 minutes
  ScriptApp.newTrigger("forwardEmails")
    .timeBased()
    .everyMinutes(2)
    .create();

  Logger.log("✅ Auto-forwarding trigger created (every 2 minutes)");
}

function removeAllTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }
  Logger.log("All triggers removed");
}
