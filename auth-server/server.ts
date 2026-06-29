import { serve } from "@hono/node-server";
import { auth } from "./auth.ts";

const port = 3000;

console.log(`🔐 Better Auth server starting on http://localhost:${port}`);

const server = serve({
  fetch: auth.handler,
  port,
  hostname: "0.0.0.0",
}, (info) => {
  console.log(`✅ Better Auth server running on http://localhost:${info.port}`);
  console.log(`📋 Health check: http://localhost:${info.port}/api/auth/ok`);
  console.log(`🔗 Auth API: http://localhost:${info.port}/api/auth/`);
});

process.on("uncaughtException", (err) => {
  console.error("Uncaught exception:", err);
});

process.on("unhandledRejection", (err) => {
  console.error("Unhandled rejection:", err);
});

// Keep the process alive
process.stdin.resume();
