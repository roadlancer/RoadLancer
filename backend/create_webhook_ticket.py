import httpx
import os
import sys

def create_ticket():
    url = "http://localhost:8000/api/support/inbound-email"
    secret = os.getenv("SUPPORT_WEBHOOK_SECRET", "roadlancer-webhook-secret-2026")
    payload = {
        "secret": secret,
        "from_email": "test-gibberish@roadlancer.com",
        "from_name": "Test User (Keyboard Mash)",
        "subject": "asdfghjkl qwertyuiop zxcvbnm 12345 florp blorp",
        "body": "fdsajkl; fdsajkl; qwertyuiop mnbvcxz\n\nblerg blop glorp glip glap! 998877665544332211\n\nzzzzzzxxxxxxccccccvvvvvvbbbbbbnnnnnnmmmmmm qqqwwweeerrrtttyyyuuuiiiooopppaaasssdddfffggghhhjjjkkklll\n\ncan u fix??? asdf asdf asdf",
        "priority": "normal",
        "source": "email"
    }

    print(f"🚀 Sending Inbound Webhook payload to {url}...")
    try:
        r = httpx.post(url, json=payload, headers={"x-webhook-secret": secret}, timeout=10.0)
        print("Status Code:", r.status_code)
        
        try:
            res_json = r.json()
            print("Response JSON:", res_json)
        except Exception:
            print("Response Text (non-JSON):", r.text)
            res_json = {}

        if r.status_code == 200 and res_json.get("success"):
            ticket_num = res_json.get("ticket_number")
            print(f"\n🎉 Success! Created Support Ticket: {ticket_num}")
            print(f"👉 You can view this ticket in your browser at /admin/support or under 'My Tickets' in the Help & Support modal.")
        else:
            print(f"\n❌ Failed to create ticket (Status {r.status_code}).")
            if r.status_code == 500:
                print("\n💡 NOTE ON 500 ERRORS: This usually means the 'support_tickets' table has not been synced to your PostgreSQL database yet.")
                print("Please run these commands inside the 'backend' folder and then restart your FastAPI server:")
                print("   npx prisma db push --schema=prisma/schema.prisma")
                print("   python -m prisma generate")
    except Exception as e:
        print("\n❌ Error connecting to backend server:", e)
        print("Please ensure your FastAPI backend server is running on http://localhost:8000")

if __name__ == "__main__":
    create_ticket()
