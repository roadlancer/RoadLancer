import { serve } from "@hono/node-server";
import { auth } from "./auth.ts";

const port = 3000;

console.log(`🔐 Better Auth server starting on http://localhost:${port}`);

serve({
  fetch: auth.handler,
  port,
  hostname: "0.0.0.0",
});

console.log(`✅ Better Auth server running on http://localhost:${port}`);
console.log(`📋 Health check: http://localhost:${port}/api/auth/ok`);
console.log(`🔗 Auth API: http://localhost:${port}/api/auth/`);
