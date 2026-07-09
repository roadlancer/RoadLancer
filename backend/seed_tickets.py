import asyncio
import random
from datetime import datetime, timedelta
import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db

REAL_LIFE_EXAMPLES = [
    # Urgent / High priority logistics & safety issues
    {
        "subject": "[URGENT] Reefer container temperature alarm on NH-48",
        "message": "The refrigerated truck carrying pharmaceutical goods shows a temperature rise above 4°C. Need immediate breakdown assistance near Surat checkpost.",
        "priority": "urgent",
        "source": "email",
    },
    {
        "subject": "Driver SOS: GPS breakdown & route diversion near Indore",
        "message": "We lost GPS tracking signal for truck KA-04-NB-4412 carrying high-value electronics. Driver phone unreachable since 2:00 AM.",
        "priority": "urgent",
        "source": "email",
    },
    {
        "subject": "Accident report & cargo inspection request #SH-9012",
        "message": "Minor collision reported near Jaipur bypass. No injuries, but rear doors dented. Need insurance survey coordinator urgently.",
        "priority": "urgent",
        "source": "web",
    },
    {
        "subject": "E-way bill mismatch detention by Commercial Tax Officer",
        "message": "Truck detained at Maharashtra-Gujarat border due to HSN code discrepancy on the e-way bill for shipment #SH-4419. Please update invoice details.",
        "priority": "high",
        "source": "email",
    },
    {
        "subject": "AI Floor price calculation error on overweight steel coils",
        "message": "The AI pricing engine suggested INR 18,000 for a 24-ton trailer from Bhilai to Mumbai, which is well below diesel cost. Please review algorithm rules.",
        "priority": "high",
        "source": "web",
    },
    {
        "subject": "Verification document rejected: RC Book renewal certificate",
        "message": "My updated RC book photo was marked rejected on the portal saying 'blurry document'. Attached high-resolution PDF copy for re-verification.",
        "priority": "high",
        "source": "web",
    },
    {
        "subject": "Payment settlement delay for Freight Invoice #INV-2026-089",
        "message": "We completed the consignment delivery 7 days ago and POD is verified, but the payout of INR 45,500 has not reflected in our bank account.",
        "priority": "high",
        "source": "email",
    },
    {
        "subject": "Request to change dropoff warehouse address mid-transit",
        "message": "Consignee requested diversion of fertilizer load from Bhiwandi warehouse #4 to Taloja industrial facility due to space constraints.",
        "priority": "high",
        "source": "web",
    },
    {
        "subject": "FASTag double deduction claim for NH-16 toll plaza",
        "message": "Our trailer was charged twice (INR 840 + INR 840) within 3 minutes at the Krishnagiri toll plaza. Requesting dispute filing and refund.",
        "priority": "normal",
        "source": "email",
    },
    {
        "subject": "Driver requested fuel advance (INR 12,000) for Kolkata route",
        "message": "Driver Rajesh Kumar requests 30% fuel allowance advance via petro-card to cover diesel expenses between Varanasi and Kolkata checkpost.",
        "priority": "normal",
        "source": "web",
    },
    {
        "subject": "GST Certificate update & Business name change request",
        "message": "Our company name changed from 'Apex Logistics Pvt Ltd' to 'Apex Global Freight Ltd'. Please update our GSTIN registration profile.",
        "priority": "normal",
        "source": "email",
    },
    {
        "subject": "POD (Proof of Delivery) digital signature stamp unreadable",
        "message": "The consignee stamp uploaded on the mobile app is slightly smudged. Can we re-upload the hard copy photo via support desk?",
        "priority": "normal",
        "source": "web",
    },
    {
        "subject": "Inquery regarding return load bidding for 20ft container",
        "message": "We have an empty 20ft container returning from Pune to Mundra port. How do we list it for return-load matching on the marketplace?",
        "priority": "normal",
        "source": "web",
    },
    {
        "subject": "Request for monthly consolidated billing statement",
        "message": "Our accounting team requires a single consolidated GST invoice for all 14 shipments completed across July 2026.",
        "priority": "normal",
        "source": "email",
    },
    {
        "subject": "Driver KYC approval pending since 48 hours",
        "message": "New driver profile for Suresh Yadav (Aadhaar ending x8891) is still under review. We need to assign him to a dispatch tomorrow morning.",
        "priority": "normal",
        "source": "web",
    },
    {
        "subject": "Vehicle type upgrade from 16-Ton to 22-Ton Multi-Axle",
        "message": "We replaced our older Eicher 16-ton truck with a Tata Signa 22-ton multi-axle vehicle. Please update our vehicle category credentials.",
        "priority": "normal",
        "source": "email",
    },
    {
        "subject": "Feedback on new AI Freight Rate estimation dashboard",
        "message": "The new price estimate breakdown chart is very helpful! Would be great if you also add historical diesel price trends over the last 6 months.",
        "priority": "low",
        "source": "web",
    },
    {
        "subject": "Question about referral program bonus for fleet owners",
        "message": "We referred another transport company with 8 trucks. When will the INR 5,000 onboarding referral credit be added to our shipper wallet?",
        "priority": "low",
        "source": "email",
    },
    {
        "subject": "How to export shipment history to CSV / Excel format?",
        "message": "Is there a button on the shipper dashboard to download our full dispatch log including origin, destination, and freight charges for tax audits?",
        "priority": "low",
        "source": "web",
    },
    {
        "subject": "Update notification email preferences & SMS alerts",
        "message": "We are receiving too many SMS alerts whenever a driver bids on our shipments. Please restrict notifications to email only during weekends.",
        "priority": "low",
        "source": "email",
    },
]

SENDERS = [
    {"name": "Test Shipper", "email": "shipper@roadlancer.com"},
    {"name": "Driver User", "email": "driver@roadlancer.com"},
    {"name": "Vikram Rathore (Apex Transport)", "email": "vikram@apextransport.in"},
    {"name": "Ananya Sharma (Vedic Agro)", "email": "ananya.sharma@vedicagro.com"},
    {"name": "Gurpreet Singh (Punjab Freight Lines)", "email": "gurpreet.singh@punjabfreight.com"},
    {"name": "Meera Iyer (Southern Logistics)", "email": "m.iyer@southernlogistics.co.in"},
    {"name": "Rajat Verma (Verma Carriers)", "email": "rajat@vermacarriers.in"},
    {"name": "Sneha Kulkarni (Deccan Pharma)", "email": "sneha.k@deccanpharma.com"},
    {"name": "Mohammed Tariq (Al-Hind Cargo)", "email": "tariq@alhindcargo.com"},
    {"name": "Dave Driver (Fleet Ops)", "email": "dave.ops@roadlancer.com"},
    {"name": "Kiran Patel (Gujarat Express)", "email": "kiran.patel@gujratexpress.in"},
    {"name": "Amitabh Bose (Bengal Traders)", "email": "a.bose@bengaltraders.com"},
    {"name": "Pooja Nair (Kerala Spice Co)", "email": "pooja.nair@keralaspice.in"},
    {"name": "Siddharth Rao (Rao Logistics)", "email": "siddharth@raologistics.com"},
    {"name": "Arjun Malhotra (National Highway Carriers)", "email": "arjun@nhcarriers.in"},
]

ADMIN_NOTES_TEMPLATES = [
    "Contacted driver via phone. Issue verified and resolution initiated.",
    "Escalated to billing and accounts department for settlement verification.",
    "Requested updated RC/DL document copies from user.",
    "AI floor price recalibrated by backend engineering team.",
    "Resolved successfully after cross-checking border checkpost logs.",
    "Pending confirmation from consignee warehouse manager.",
    "Reviewed verification photos using OCR. Approved.",
    None,
    None,
    None,
]

async def seed_100_tickets():
    print("🔌 Connecting to database...")
    if not db.is_connected():
        await db.connect()
    
    print("🧹 Cleaning existing support tickets...")
    deleted = await db.support_tickets.delete_many()
    print(f"✅ Deleted {deleted} existing tickets.")

    # Fetch existing users to link tickets where possible
    users = await db.user.find_many()
    user_map_by_email = {u.email.lower(): u.id for u in users}
    all_user_ids = [u.id for u in users] if users else [None]

    print("🚀 Generating 100 diversified support tickets...")
    
    statuses = ["open", "in_progress", "resolved", "closed"]
    status_weights = [0.35, 0.25, 0.25, 0.15]  # Realistic mix

    priorities = ["urgent", "high", "normal", "low"]
    priority_weights = [0.10, 0.25, 0.50, 0.15]

    sources = ["email", "web"]
    source_weights = [0.55, 0.45]

    now = datetime.utcnow()
    created_tickets = []

    for i in range(1, 101):
        # Generate ticket number TICK-1001 to TICK-1100 or random 4-digit
        ticket_number = f"TICK-{1000 + i}"

        # Choose base example or create dynamic variation
        example = random.choice(REAL_LIFE_EXAMPLES)
        sender = random.choice(SENDERS)
        
        # Link to real user if email matches or randomly assign some to known users
        user_id = user_map_by_email.get(sender["email"].lower())
        if not user_id and random.random() < 0.4 and all_user_ids:
            user_id = random.choice(all_user_ids)

        # Diversify subject slightly with route or truck numbers
        subject = example["subject"]
        if "NH-48" in subject and i % 2 == 0:
            subject = subject.replace("NH-48", f"NH-{random.choice([16, 44, 52, 66])}")
        if "#SH-" in subject:
            subject = f"{subject.split('#SH-')[0]}#SH-{random.randint(1000, 9999)}"

        # Diversify attributes
        priority = random.choices(priorities, weights=priority_weights, k=1)[0]
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        source = random.choices(sources, weights=source_weights, k=1)[0]
        
        # Override priority from example sometimes, or keep dynamic
        if example.get("priority") in ["urgent", "high"] and random.random() < 0.7:
            priority = example["priority"]

        # Spread timestamps over the last 30 days
        days_ago = random.uniform(0, 30)
        created_at = now - timedelta(days=days_ago)
        
        # If status is resolved/closed, updatedAt should be later than createdAt
        updated_at = created_at
        if status in ["resolved", "closed"]:
            updated_at = created_at + timedelta(hours=random.uniform(2, 48))

        admin_notes = random.choice(ADMIN_NOTES_TEMPLATES) if status in ["in_progress", "resolved", "closed"] else None

        created_tickets.append({
            "ticketNumber": ticket_number,
            "senderEmail": sender["email"].lower(),
            "senderName": sender["name"],
            "subject": f"[{priority.upper()}] {subject}" if priority in ["urgent", "high"] and not subject.startswith("[") else subject,
            "message": f"{example['message']}\n\nRef ID: RL-2026-{random.randint(10000, 99999)}\nSent from RoadLancer {source.upper()} Gateway.",
            "status": status,
            "priority": priority,
            "source": source,
            "userId": user_id,
            "adminNotes": admin_notes,
            "createdAt": created_at,
            "updatedAt": updated_at,
        })

    # Sort chronologically before inserting so IDs or queries are nicely ordered
    created_tickets.sort(key=lambda x: x["createdAt"])

    # Insert sequentially or in batches
    count = 0
    for t_data in created_tickets:
        await db.support_tickets.create(data=t_data)
        count += 1
        if count % 20 == 0:
            print(f"⏳ Inserted {count}/100 tickets...")

    print(f"\n🎉 Successfully created {count} real-life, diversified support tickets!")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_100_tickets())
