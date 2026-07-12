import httpx
import os
import time

def send_kb_webhook_ticket():
    url = "http://localhost:8000/api/support/inbound-email"
    secret = os.getenv("SUPPORT_WEBHOOK_SECRET", "roadlancer-webhook-secret-2026")

    # This payload matches Q1.1 of knowledge-base.md exactly:
    # "Shipper or driver reports that toll charges (e.g., ₹4,850 or standard axle toll) were deducted twice from their RoadLancer FASTag / wallet at a checkpost or toll plaza."
    payload = {
        "secret": secret,
        "from_email": "accounts@freightmasters.in",
        "from_name": "Suresh Mehta (Accounts Manager)",
        "subject": "[FASTag Dispute] Double toll deduction of ₹4,850 at Khed Shivapur toll plaza",
        "body": "Hello Support Team,\n\nOur vehicle MH-12-PQ-4455 passed through the Khed Shivapur toll plaza today at 04:15 AM on trip #SH-9921.\nOur RoadLancer wallet was double debited for ₹4,850 instead of the standard commercial toll rate of ₹2,425.\nWe have attached the NPCI SMS confirmation and FASTag transaction ID #FT-88392019.\nPlease clarify when this duplicate debit will be refunded back to our wallet automatically or if we need to take action.",
        "priority": "high",
        "source": "email"
    }

    print("==================================================================================")
    print("🚀 SENDING WEBHOOK TICKET (MATCHING KNOWLEDGE BASE Q1.1: FASTAG DOUBLE DEDUCTION)")
    print("==================================================================================")
    print(f"Target URL: {url}")
    print(f"From:       {payload['from_name']} <{payload['from_email']}>")
    print(f"Subject:    {payload['subject']}")
    print("-" * 82)

    try:
        r = httpx.post(url, json=payload, headers={"x-webhook-secret": secret}, timeout=10.0)
        res_json = r.json() if r.status_code == 200 else {}

        if r.status_code == 200 and res_json.get("success"):
            ticket_num = res_json.get("ticket_number")
            ticket_id = res_json.get("ticket", {}).get("id")
            print(f"✅ Webhook Ticket Created Successfully!")
            print(f"   • Ticket Number: #{ticket_num}")
            print(f"   • Initial Status: new")
            print(f"   • Background AI Classification & KB Auto-Resolution Dispatched!")
            print("\n👀 Lifecycle Summary:")
            print(f"   1. Created with status = 'new'")
            print(f"   2. Background worker transitions to status = 'processing' during KB check")
            print(f"   3. AI finds match in knowledge-base.md (Q1.1 FASTag Double Deduction)")
            print(f"   4. AI automatically replies with the official KB resolution answer and marks status = 'resolved'")
        else:
            print(f"❌ Webhook Failed (HTTP {r.status_code}): {r.text}")
    except Exception as e:
        print(f"❌ Could not connect to backend at {url}: {e}")
        print("\nEnsure both servers are running:")
        print("  1. Terminal 1 (auth-server): cd auth-server && bun --watch server.ts")
        print("  2. Terminal 2 (backend):     cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    send_kb_webhook_ticket()
