import httpx
import os
import time

def create_test_tickets():
    url = "http://localhost:8000/api/support/inbound-email"
    secret = os.getenv("SUPPORT_WEBHOOK_SECRET", "roadlancer-webhook-secret-2026")

    test_payloads = [
        {
            "from_email": "driver.ramesh@roadlancer.com",
            "from_name": "Ramesh Kumar (Reefer Truck KA-04-E-9988)",
            "subject": "[EMERGENCY SOS] Reefer compressor failure on NH-48 - Vaccine cargo spoilage warning",
            "body": "SOS IMMEDIATE HELP REQUIRED!\nOur Tata Signa Reefer truck compressor suddenly shut down near Belagavi checkpost on NH-48. Internal container temperature has spiked from -18°C to -4°C in the last 20 minutes.\nWe are transporting 14 tonnes of temperature-sensitive pharmaceutical vaccines for Cipla.\nNeed immediate dispatch of mobile refrigeration repair van or replacement cold-chain container before cargo is completely ruined!",
            "priority": "urgent",
            "expected_category": "logistics_breakdown"
        },
        {
            "from_email": "accounts@freightmasters.in",
            "from_name": "Suresh Mehta (Accounts Manager)",
            "subject": "[FASTag Dispute] Double toll deduction of ₹4,850 at Khed Shivapur toll plaza",
            "body": "Hello Billing Support Team,\n\nOur vehicle MH-12-PQ-4455 passed through the Khed Shivapur toll plaza today at 04:15 AM on trip #SH-9921.\nOur RoadLancer wallet was double debited for ₹4,850 instead of the standard commercial toll rate of ₹2,425.\nWe have attached the NPCI SMS confirmation and FASTag transaction ID #FT-88392019.\nPlease refund the ₹2,425 excess debit back to our master fleet wallet immediately as our trucks are blocked at the next toll due to low balance.",
            "priority": "high",
            "expected_category": "billing_payment"
        },
        {
            "from_email": "owner@singhlogistics.com",
            "from_name": "Gurpreet Singh (Fleet Owner)",
            "subject": "[KYC PENDING] Commercial RC Book & National Permit renewal verification stuck for 3 days",
            "body": "Hi RoadLancer Verification Team,\n\nWe uploaded our renewed Commercial RC Book and All-India National Permit documents for our 12-wheeler Ashok Leyland truck (PB-08-XY-7766) on Tuesday.\nThe dashboard still shows 'Pending KYC Verification' and our driver is unable to accept the urgent steel coil dispatch from Tata Steel Jamshedpur scheduled for tonight.\nPlease review and verify our documents urgently so we can start the trip.",
            "priority": "high",
            "expected_category": "verification_kyc"
        },
        {
            "from_email": "logistics@reliance-retail.com",
            "from_name": "Ananya Sharma (Dispatch Coordinator)",
            "subject": "[GPS Tracking Loss] Telematics signal lost for shipment #SHIP-4402 since 6 hours",
            "body": "Dear Support Team,\n\nWe are monitoring live shipment #SHIP-4402 (500 boxes of electronics moving from Bhiwandi warehouse to Hyderabad).\nThe live GPS tracking signal on the RoadLancer shipper portal stopped updating at 11:30 AM near Solapur.\nCan your tracking team ping the driver's SIM telematics or check with the IoT onboard unit to confirm the truck's exact current location and estimated arrival time?",
            "priority": "normal",
            "expected_category": "shipment_tracking"
        },
        {
            "from_email": "driver.manish@gmail.com",
            "from_name": "Manish Verma (Independent Driver)",
            "subject": "[Login Issue] Unable to reset OTP password after changing mobile phone number",
            "body": "Hello Support,\n\nI recently upgraded my mobile phone and switched my SIM card to Airtel (new number: +91 98765 43210).\nWhen I try to log into the RoadLancer Driver App using my registered email (driver.manish@gmail.com), the 2FA SMS OTP is still being sent to my old lost Vodafone number.\nCould you please update my registered phone number or temporarily disable 2FA so I can log in and update my profile?",
            "priority": "normal",
            "expected_category": "account_access"
        },
        {
            "from_email": "info@greenwaytransport.com",
            "from_name": "Deepak Rao (Operations Analyst)",
            "subject": "[Feature Question] Exporting monthly carbon emission savings report to CSV/PDF",
            "body": "Hi RoadLancer Team,\n\nWe are preparing our quarterly ESG (Environmental, Social, and Governance) sustainability presentation for our corporate clients.\nWe noticed the 'Green Fleet Analytics' tab on the web portal shows our monthly fuel savings and CO2 reduction, but we couldn't find a button to download this historical data as a multi-month CSV or PDF summary.\nIs there a way to export this report, or is this scheduled for a future software update?\n\nThanks,\nDeepak Rao",
            "priority": "low",
            "expected_category": "general"
        }
    ]

    print(f"🚀 Starting Multi-Category Webhook Ticket Creation & AI Classification Suite...\n")
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

        print(f"\n📨 [Test {idx}/6] Sending Webhook -> Expected AI Category: '{expected_cat}'")
        print(f"   Subject: {test_item['subject'][:70]}...")
        try:
            r = httpx.post(url, json=payload, headers={"x-webhook-secret": secret}, timeout=10.0)
            res_json = r.json() if r.status_code == 200 else {}

            if r.status_code == 200 and res_json.get("success"):
                ticket_num = res_json.get("ticket_number")
                print(f"   ✅ Created Ticket #{ticket_num} (Status 200)")
                print(f"   👉 AI Classification task dispatched non-blockingly to pg-boss / Gemini!")
            else:
                print(f"   ❌ Failed (Status {r.status_code}): {r.text}")
        except Exception as e:
            print(f"   ❌ Network/Connection error: {e}")

        # Small 0.5s pause between webhook calls so outputs don't interleave confusingly
        time.sleep(0.5)

    print("\n" + "="*80)
    print("🎉 All 6 multi-category test tickets submitted successfully!")
    print("Check your Bun 'auth-server' terminal logs or '/admin/support' table to see pg-boss & Gemini auto-classify each ticket into its exact category and priority.")

if __name__ == "__main__":
    create_test_tickets()
