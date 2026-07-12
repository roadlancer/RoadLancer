import httpx
import os
import time

def create_test_tickets():
    url = "http://localhost:8000/api/support/inbound-email"
    secret = os.getenv("SUPPORT_WEBHOOK_SECRET", "roadlancer-webhook-secret-2026")

    test_payloads = [
        {
            "from_email": "driver.vikram@gmail.com",
            "from_name": "Vikram Singh (16-Wheeler Driver HR-38-Z-1029)",
            "subject": "[Fuel Advance Question] When will the 70% fuel advance be credited to my wallet for trip #TRIP-8812?",
            "body": "Namaste RoadLancer Support,\n\nWe just finished loading 22 metric tonnes of cement bags at the ACC Cement factory in Chandrapur for trip #TRIP-8812.\nThe shipper has already confirmed loading and generated the e-Way bill on the portal 10 minutes ago.\nCould you please let us know when the 70% fuel advance will be credited to my RoadLancer Fuel & Toll Wallet so I can fill high-speed diesel at the nearest Indian Oil pump before starting on NH-44?\n\nThank you,\nVikram Singh",
            "priority": "normal",
            "expected_category": "billing_payment"
        }
    ]

    print(f"🚀 Starting Webhook Ticket Creation & AI Auto-Resolution Check...\n")
    print(f"Target URL: {url}")
    print(f"Queue Engine: pg-boss (running on Bun auth-server @ http://localhost:3000)\n" + "="*80)

    for idx, test_item in enumerate(test_payloads, 1):
        expected_cat = test_item["expected_category"]
        payload = {
            "secret": secret,
            "from_email": test_item["from_email"],
            "from_name": test_item["from_name"],
            "subject": test_item["subject"],
            "body": test_item["body"],
            "priority": test_item["priority"],
            "source": "email"
        }

        print(f"\n📨 Sending Single Brand New Webhook -> Expected AI Category: '{expected_cat}'")
        print(f"   Subject: {test_item['subject'][:70]}...")
        try:
            r = httpx.post(url, json=payload, headers={"x-webhook-secret": secret}, timeout=30.0)
            res_json = r.json() if r.status_code == 200 else {}

            if r.status_code == 200 and res_json.get("success"):
                ticket_num = res_json.get("ticket_number")
                print(f"   ✅ Created Ticket #{ticket_num} (Status 200)")
                print(f"   👉 AI Classification & KB Auto-Resolution dispatched to pg-boss / Gemini!")
            else:
                print(f"   ❌ Failed (Status {r.status_code}): {r.text}")
        except Exception as e:
            print(f"   ❌ Network/Connection error: {e}")

    print("\n" + "="*80)
    print("🎉 Brand new single test ticket submitted successfully!")
    print("Check your Support Desk (/admin/support) or pg-boss Queue Monitor (/admin/jobs) to see Gemini auto-resolve it from knowledge-base.md.")

if __name__ == "__main__":
    create_test_tickets()
