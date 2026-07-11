import asyncio
import random
from datetime import datetime, timedelta
import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db

# 20 realistic alternating replies (Customer -> Agent -> Customer -> Agent...)
# Each reply has at least 10 lines of detailed text representing a thorough logistics investigation.
REPLIES_DATA = [
    # 1. Customer (Index 0)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hello RoadLancer Support Team,",
            "",
            "We are experiencing a critical temperature alarm on our refrigerated trailer carrying temperature-sensitive pharmaceutical vaccines.",
            "Vehicle Registration: MH-04-EK-9912 (Reefer Unit #4)",
            "Current Location: NH-48 Highway, approximately 15 km before the Surat South Checkpost.",
            "Consignment ID: RL-PHARMA-2026-8819 (Assigned to Pfizer Distribution Center Mumbai)",
            "The telematics sensor on our dashboard just triggered a Level-2 alert indicating the internal cargo temperature has risen from 2.1°C to 5.4°C over the past 45 minutes.",
            "Our driver, Mr. Santosh Yadav, reports that the primary compressor unit is making an unusual grinding noise and the auxiliary cooling fan has stopped spinning.",
            "If the ambient internal temperature exceeds 8.0°C for more than 2 hours, the entire vaccine batch valued at INR 42 Lakhs will be rendered unusable under CDSCO regulatory guidelines.",
            "We urgently require immediate emergency roadside breakdown assistance or a replacement reefer container dispatch to transfer the cargo before spoilage occurs.",
            "",
            "Please advise immediately on emergency protocol step #1.",
            "Regards,",
            "Rajesh Kumar | Fleet Operations Lead | Apex Pharma Logistics"
        ]
    },
    # 2. Agent (Index 1)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "Thank you for contacting RoadLancer Emergency Support. I have escalated this ticket to our Priority-1 Logistics Breakdown Desk immediately.",
            "I have pulled up telemetry live feeds from your IoT sensor cluster (MH-04-EK-9912) on our internal command center dashboard.",
            "Here is what our diagnostic system indicates right now:",
            "- Current Internal Temperature: 5.6°C (+0.2°C over the last 10 minutes)",
            "- Compressor Motor RPM: Fluctuating dangerously between 1,200 and 1,800 RPM (Normal is 2,400 RPM)",
            "- Ambient Outside Highway Temperature: 34.2°C near Surat checkpost",
            "I have already notified our certified mobile reefer technician network in Surat (ColdChain Tech Services Pvt Ltd).",
            "They have an emergency repair van currently located near Sachin Industrial Area, just 12 km north of your driver's exact GPS coordinates.",
            "To expedite the dispatch of the repair van, could you please confirm if Mr. Santosh has pulled over into a safe service lane off NH-48?",
            "Also, please instruct the driver NOT to open the rear insulated cargo doors under any circumstances, as opening the doors will cause an immediate spike of 3°C to 4°C within minutes.",
            "",
            "Best regards,",
            "Sarah Jenkins",
            "RoadLancer Priority Desk"
        ]
    },
    # 3. Customer (Index 2)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "Thank you for the prompt response and accurate remote diagnostics. That is a huge relief.",
            "I just spoke to our driver, Mr. Santosh Yadav, via satellite phone and confirmed his exact positioning.",
            "He has parked safely at the Indian Oil Highway Service Station (Milestone 242, NH-48 Southbound, near Kadodara Junction).",
            "He confirms that the rear cargo doors are double-locked and sealed with the original electronic tamper-proof bolt (#SEAL-889102).",
            "He noticed that the alternator belt connecting the diesel auxiliary engine to the compressor pulley appears loose and is slipping significantly under load.",
            "The onboard digital display on the ThermoKing controller is flashing Error Code E-44 (Low Refrigerant Pressure / Drive Slip).",
            "Please dispatch the certified technician from ColdChain Tech Services immediately to this petrol pump location.",
            "Can you provide us with the technician's name, mobile number, and estimated time of arrival (ETA) so Santosh can coordinate directly upon arrival?",
            "We have about 65 minutes left before the thermal buffer inside the insulated walls begins degrading towards the critical 8°C mark.",
            "",
            "Awaiting your dispatch confirmation.",
            "Rajesh Kumar"
        ]
    },
    # 4. Agent (Index 3)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "I have dispatched the ColdChain Tech Services emergency mobile unit directly to Milestone 242 (Indian Oil Station, Kadodara Junction).",
            "Here are the dispatch and technician details for your records and driver coordination:",
            "1. Lead Certified Technician: Mr. Vikram Patel (ID: CCTS-GUJ-104)",
            "2. Technician Mobile Phone: +91 98240-55192",
            "3. Service Vehicle: Mahindra Bolero Pickup (Reg: GJ-05-SR-3310) equipped with ThermoKing parts & R-404A refrigerant cylinders.",
            "4. Confirmed ETA: 22 minutes (Currently en route via Surat-Bardoli link road, clear traffic reported).",
            "I have briefed Vikram directly on Error Code E-44 and the drive belt slippage observation.",
            "He is carrying replacement serpentine belts (Part #TK-9921) and a high-pressure manifold gauge to check if any R-404A coolant was lost during the drive slip.",
            "In the meantime, I have enabled High-Frequency Telemetry Polling (every 30 seconds instead of 5 minutes) on your container to monitor the temperature curve continuously.",
            "Current temperature reading stands at 5.9°C. The insulation rate of climb has slowed down slightly because the vehicle is parked in the shade of the fuel station canopy.",
            "I will continue monitoring from our end until Vikram arrives on-site.",
            "",
            "Best regards,",
            "Sarah Jenkins | RoadLancer Support"
        ]
    },
    # 5. Customer (Index 4)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "Driver Santosh just informed me that Mr. Vikram Patel (Technician) has arrived safely at the Indian Oil service station.",
            "Vikram inspected the drive mechanism and confirmed your preliminary diagnosis regarding Error Code E-44.",
            "The main drive belt had suffered thermal wear and partially frayed, causing the compressor clutch to disengage intermittently.",
            "Vikram is currently removing the frayed belt and installing the heavy-duty replacement belt (Part #TK-9921) right now.",
            "However, while inspecting the compressor housing, he noted that the R-404A refrigerant line gauge shows 180 PSI, whereas nominal operating pressure for a -2°C setpoint requires 240 PSI.",
            "He recommends performing a quick 15-minute top-up of R-404A refrigerant to ensure the compressor can pull down the temperature rapidly once restarted.",
            "The additional cost for the refrigerant top-up plus standard labor is estimated at INR 4,500 on top of our existing RoadLancer Roadside Shield coverage.",
            "Can RoadLancer Support authorize this supplemental INR 4,500 charge directly against our corporate wallet balance (#WALLET-APEX-09)?",
            "We want Vikram to proceed without any delay to start the rapid pulldown cycle immediately.",
            "",
            "Please confirm wallet pre-authorization.",
            "Rajesh Kumar"
        ]
    },
    # 6. Agent (Index 5)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "I have instantly processed and approved the pre-authorization for the supplemental INR 4,500 charge against Corporate Wallet #WALLET-APEX-09.",
            "Authorization Reference Code: AUTH-2026-RL-77410",
            "I have transmitted this authorization directly to ColdChain Tech Services via our vendor portal, so Mr. Vikram Patel can proceed with the R-404A refrigerant top-up immediately.",
            "Our automated billing system will reflect this charge on your monthly consolidated billing statement under 'Emergency Roadside Consumables'.",
            "Regarding the temperature trajectory:",
            "- At 14:12 IST, just before belt replacement started, internal temperature peaked at 6.3°C.",
            "- This remains well below the CDSCO mandatory limit of 8.0°C, meaning zero regulatory deviation has occurred so far.",
            "Once Vikram completes the belt tensioning and refrigerant charging, please instruct Santosh to set the ThermoKing controller to 'Rapid Freeze / High-Duty Cycle' mode for the first 30 minutes.",
            "This will force the evaporator fans at 100% capacity and bring the cargo core back down to the target 2.0°C threshold as quickly as possible.",
            "Please let me know as soon as the unit powers back on and the compressor engages.",
            "",
            "Warm regards,",
            "Sarah Jenkins | RoadLancer Priority Desk"
        ]
    },
    # 7. Customer (Index 6)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "Fantastic news! The repairs and refrigerant charging were completed successfully at 14:28 IST.",
            "Vikram tensioned the new belt to exact factory specifications and recharged the R-404A loop to 245 PSI.",
            "When Santosh switched on the auxiliary diesel engine, the ThermoKing unit booted up smoothly with zero error codes on the digital display.",
            "We activated the 'Rapid Freeze / High-Duty Cycle' mode exactly as you instructed.",
            "Within the first 12 minutes of operation, our driver reported that the discharge air temperature dropping out of the ceiling duct reached -1.5°C.",
            "The ambient cargo cabin reading on the external digital thermometer has already dropped from 6.3°C down to 4.8°C and continues to fall steadily.",
            "Vikram is performing a final 10-minute leak check using an electronic halogen leak detector around the compressor fittings right now to ensure no micro-leaks remain.",
            "We would like to request a formal digital Incident Diagnostic Report (IDR) signed by RoadLancer and ColdChain Tech Services once this ticket is wrapped up.",
            "Our Quality Assurance (QA) auditor requires this documentation to attach to the electronic Batch Delivery Record for Pfizer.",
            "",
            "Thanks again for the lightning-fast support and wallet coordination.",
            "Rajesh Kumar"
        ]
    },
    # 8. Agent (Index 7)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "That is wonderful to hear! Our live IoT telemetry feed is mirroring your exact field observations right now:",
            "- Current Internal Temperature: 4.2°C (Downward slope of -0.3°C per 5 minutes)",
            "- Compressor Discharge Pressure: Stable at 244 PSI",
            "- Evaporator Fan Air Velocity: 100% nominal flow rate",
            "Regarding your request for the formal Incident Diagnostic Report (IDR) for your QA auditor and Pfizer records:",
            "I have already generated the draft IDR #IDR-2026-NH48-1001 inside our compliance portal.",
            "The report automatically logs:",
            "1. Minute-by-minute temperature graphs from our tamper-proof IoT gateway from 12:00 IST through current recovery.",
            "2. Verification that temperature never exceeded 6.3°C (preserving the 2°C-8°C cold chain envelope throughout the entire incident).",
            "3. Certified technician sign-off from Mr. Vikram Patel detailing belt replacement and R-404A top-up (Part #TK-9921, Auth #AUTH-2026-RL-77410).",
            "4. GPS timestamped location verification confirming zero door openings or seal breakages (#SEAL-889102 intact).",
            "I will finalize and attach the digitally signed PDF copy directly to this support thread once the temperature stabilizes below 2.5°C.",
            "Is the vehicle ready to resume transit towards Mumbai now?",
            "",
            "Best regards,",
            "Sarah Jenkins"
        ]
    },
    # 9. Customer (Index 8)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "Yes, Vikram just signed off on the job card and departed from the service station after confirming zero halogen leaks around the manifold seals.",
            "Driver Santosh has conducted his standard pre-departure safety walkaround and checked all 18 tires and air brakes.",
            "He has just pulled out of the Indian Oil service station and re-entered the southbound carriageway of NH-48 heading towards Vapi and Mumbai.",
            "Our internal dashboard reading shows that the temperature has now reached 2.4°C, which is well within our target operating corridor of 2.0°C to 3.0°C.",
            "We have instructed Santosh to maintain a steady cruising speed and avoid harsh acceleration to prevent any mechanical stress on the newly installed belt during its initial break-in period.",
            "However, we noticed one minor discrepancy on the shipper tracking map on our web portal:",
            "While the temperature telemetry is updating every 30 seconds, the GPS icon on the map appears to be stuck at the Kadodara service station milestone.",
            "Could you please check if the GPS tracking module (SIM card slot #2 on the telematics unit) requires a remote reset after the high-frequency polling activation?",
            "We need live GPS tracking to remain active for our automated geofence arrival alerts at the Pfizer Bhiwandi warehouse.",
            "",
            "Looking forward to your check on the GPS tracking sync.",
            "Rajesh Kumar"
        ]
    },
    # 10. Agent (Index 9)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "Good catch on the GPS tracking display! I immediately investigated the telematics gateway configuration on our server side.",
            "When we enabled High-Frequency Telemetry Polling earlier, the primary data channel prioritized the RS-232 serial bus transmitting the ThermoKing temperature registers over the cellular packet queue.",
            "This caused the GPS NMEA coordinate packets to buffer locally inside the telematics unit memory instead of pushing instantly to the web socket relay.",
            "I have just executed a soft remote command (`AT+SGNSS_FLUSH=1`) from our engineering console to clear the packet queue and re-balance the dual SIM data streams.",
            "Diagnostic results following the remote reset:",
            "- GPS Fix Status: 3D High-Precision Fix (12 satellites tracked via NavIC + GPS constellations)",
            "- Current Coordinates: 21.0824° N, 72.9341° E (Moving Southbound on NH-48 near Navsari bypass at 58 km/h)",
            "- Temperature Feed: 2.2°C (Perfectly stable and regulated)",
            "Please refresh your shipper portal dashboard or press Ctrl+F5 on your browser.",
            "You should now see the live green truck icon moving smoothly along the highway with real-time speed and heading updates restored.",
            "Can you verify that your geofence triggers for Bhiwandi are displaying correctly now?",
            "",
            "Best regards,",
            "Sarah Jenkins | RoadLancer Command Desk"
        ]
    },
    # 11. Customer (Index 10)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "I refreshed the shipper dashboard on both our desktop browser and the RoadLancer iOS Fleet App.",
            "The live green truck icon is back online! We can see MH-04-EK-9912 cruising past the Navsari toll plaza right now at 62 km/h with the temperature holding solid at 2.2°C.",
            "Our automated geofence ETA calculator has updated seamlessly and now projects arrival at the Pfizer Bhiwandi Logistics Park at exactly 19:45 IST tonight.",
            "I also double-checked our automated webhook alerts configured for our internal Slack channel `#apex-live-consignments`.",
            "The webhooks just successfully received the `CONSIGNMENT_TRANSIT_RESUMED` payload with the updated coordinates and temperature attributes.",
            "Everything on the live tracking and monitoring front is working at 100% perfection.",
            "Before we conclude the operational phase of this ticket, there is one financial query regarding the billing settlement for the FASTag toll charges during this detour:",
            "Because Santosh had to take the Kadodara service road loop twice to meet the repair van and turn around, our ICICI bank FASTag account logged two additional toll deductions totaling INR 310.",
            "Since this detour was strictly mandated for emergency roadside repair under the RoadLancer Shield guarantee, can we add this INR 310 credit to our invoice adjustment list as well?",
            "We want our monthly ledger accounting to balance cleanly without manual credit notes later.",
            "",
            "Please let us know on the FASTag credit process.",
            "Rajesh Kumar"
        ]
    },
    # 12. Agent (Index 11)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "I am delighted to confirm that live GPS tracking and Slack webhook integrations are fully synchronized and performing flawlessly.",
            "Regarding the INR 310 FASTag toll deduction incurred during the emergency repair loop at Kadodara:",
            "You are absolutely correct. Under Section 4.2 of the RoadLancer Priority Shield Service Level Agreement (SLA), any mandatory highway detours or toll loops necessitated by an authorized roadside mechanical breakdown are 100% reimbursable.",
            "I have just submitted Credit Adjustment Voucher #CREDIT-TOLL-2026-901 directly to your account ledger.",
            "Here is how it will be processed:",
            "1. Credit Amount: INR 310.00 (Tax Exempt Reimbursement)",
            "2. Ledger Account: Apex Pharma Logistics Corporate Wallet (#WALLET-APEX-09)",
            "3. Status: Approved & Posted (Reflecting immediately in your usable balance)",
            "4. Invoice Mapping: Automatically offset against your upcoming July 2026 Freight Billing Statement.",
            "I have verified your wallet summary screen, and the available balance has increased by INR 310 as of 15:10 IST today.",
            "You can download the instant credit advice slip directly from the `Billing -> Credit Vouchers` tab on your dashboard.",
            "We are committed to ensuring you incur zero hidden out-of-pocket expenses when dealing with emergency transit situations on our network.",
            "Let me know if your accounting team requires a separate signed PDF memo for this credit.",
            "",
            "Warm regards,",
            "Sarah Jenkins"
        ]
    },
    # 13. Customer (Index 12)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "Thank you! Our accounting officer just checked the `Billing -> Credit Vouchers` tab and confirmed that Credit Voucher #CREDIT-TOLL-2026-901 is already posted and visible.",
            "That is exceptionally transparent and hassle-free accounting support.",
            "We are now tracking the vehicle as it approaches the Maharashtra border checkpost at Talasari (Milestone 138).",
            "Usually, commercial vehicles carrying pharmaceutical products undergo a mandatory e-way bill barcode scan and temperature seal verification at this interstate border post.",
            "To prevent any unnecessary detention or delays at the RTO booth, could you please push the digital e-way bill copy (#EWB-2026-MH-44910) and our freshly generated Incident Diagnostic Report (IDR) to the driver's RoadLancer Mobile App?",
            "When Santosh presents the QR code on his tablet to the border excise inspector, having the official RoadLancer breakdown IDR attached digitally will explain why the vehicle stopped for 80 minutes in Gujarat.",
            "Excise inspectors can sometimes raise queries if the GPS transit duration between Surat and Talasari exceeds standard transit norms by more than an hour.",
            "Having the digital IDR pre-attached to the e-way bill QR code will guarantee a smooth 2-minute green-channel clearance at the checkpost.",
            "",
            "Please confirm once the digital documents are pushed to Santosh's driver terminal.",
            "Rajesh Kumar"
        ]
    },
    # 14. Agent (Index 13)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "That is a brilliant proactive foresight! Interstate excise checkposts do frequently cross-reference transit durations against e-way bill timestamps.",
            "I have just completed the digital document attachment and pushed the synchronized bundle to Mr. Santosh Yadav's RoadLancer Driver App (Terminal ID: DRV-MH-04-9912).",
            "Here is what has been injected into his digital wallet right now:",
            "1. Primary E-Way Bill PDF: #EWB-2026-MH-44910 (Barcode & QR Code active and verified against NIC GST portal).",
            "2. Certified Incident Diagnostic Report (IDR): #IDR-2026-NH48-1001 bearing the official RoadLancer Digital Trust Seal and ColdChain Tech Services maintenance sign-off.",
            "3. GPS Geofence Log Annexure: Demonstrating that vehicle remained stationary only within the Indian Oil service plaza and never deviated into unauthorized cargo transfer zones.",
            "When the RTO or Excise Inspector scans the QR code on Santosh's tablet using the government `e-Way Bill Verification` app, the system will automatically display the green badge: `TRANSIT DELAY VERIFIED: EMERGENCY ROADSIDE REPAIR`.",
            "Furthermore, I have sent an SMS alert to Santosh's registered mobile number instructing him to keep the tablet screen set to maximum brightness when entering the Talasari commercial vehicle lane.",
            "Our automated checkpost assistant will log the exact entry and exit timestamps as he passes through the gates.",
            "Please let us know once he clears the Talasari border without issues.",
            "",
            "Best regards,",
            "Sarah Jenkins | RoadLancer Support"
        ]
    },
    # 15. Customer (Index 14)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "Santosh just crossed the Talasari interstate checkpost at 16:40 IST! It was exactly as smooth as you predicted.",
            "He pulled into Commercial Lane #3 where the excise inspector scanned the QR code on his tablet.",
            "The inspector saw the green verified breakdown badge and the digital IDR annexure instantly on his terminal screen.",
            "He checked the physical seal number (#SEAL-889102) on the rear doors, verified that it matched the e-way bill manifest exactly, and waved our truck through in less than 90 seconds!",
            "Santosh did not even have to step out of the cabin or open any paper folders. That digital integration saved us easily 45 minutes of manual explanation.",
            "The vehicle is now cruising past Manor on NH-48 heading towards Virar and Bhiwandi.",
            "Current internal temperature reading is holding steady at 2.1°C with compressor duty cycle dropping back to a highly efficient 35% eco-mode.",
            "We have already alerted the warehouse receiving team at Pfizer Bhiwandi Bay #12 that the truck is on track for its 19:45 IST unloading slot.",
            "Everything is looking completely solid right now.",
            "We will send one final update once the truck docks at Bay #12 and the unloading inspection commences.",
            "",
            "Thank you so much for your outstanding coordination across every single step today.",
            "Rajesh Kumar"
        ]
    },
    # 16. Agent (Index 15)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "That is truly exhilarating news! Hearing that our automated QR verification and digital IDR annexure delivered a 90-second green-channel clearance at Talasari makes our entire engineering and support team incredibly proud.",
            "I am monitoring the live telematics dashboard as MH-04-EK-9912 navigates the Manor-Virar stretch:",
            "- Speed: 56 km/h (Steady highway flow)",
            "- Cargo Core Temperature: 2.1°C (Zero variance over the last 90 minutes)",
            "- Compressor Eco-Mode: Functioning at peak thermal efficiency with minimal fuel draw",
            "- Battery & Alternator Voltage: 27.8 Volts (Confirming the new drive belt is generating perfect charging current)",
            "To prepare for the upcoming docking at Pfizer Bhiwandi Bay #12:",
            "I have configured an automated `Pre-Arrival Cold Chain Summary` trip data packet.",
            "Exactly 15 minutes before Santosh enters the Bhiwandi warehouse geofence, our server will automatically email the complete trip temperature log (in both CSV and digitally signed PDF formats) directly to:",
            "1. `qa.receiving@pfizer.com` (Pfizer Bhiwandi Quality Assurance Desk)",
            "2. `logistics@apexpharma.in` (Your internal operations team)",
            "This ensures that by the time the truck backs up to the unloading bay, the warehouse inspectors will already have verified that the vaccine batch experienced 100% compliant cold-chain storage throughout the journey.",
            "I will keep this ticket open and actively monitored until final unloading and sign-off at Bay #12.",
            "",
            "Warmest regards,",
            "Sarah Jenkins"
        ]
    },
    # 17. Customer (Index 16)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "Update: Truck MH-04-EK-9912 docked safely at Pfizer Bhiwandi Logistics Park Bay #12 at exactly 19:42 IST (3 minutes ahead of our projected schedule!).",
            "The Pfizer Quality Assurance manager, Dr. Arvind Mehta, was waiting at the docking bay with his inspection team.",
            "He confirmed that the automated `Pre-Arrival Cold Chain Summary` email arrived inside his inbox at 19:27 IST as programmed.",
            "They inspected the electronic tamper-proof seal (#SEAL-889102), verified the digital signature on the continuous temperature log, and opened the rear doors under controlled dock conditions.",
            "Internal core temperature of the vaccine master cartons was measured using their calibrated infrared probes at exactly 2.2°C across all 18 pallets.",
            "Dr. Mehta signed off on the electronic Proof of Delivery (e-POD) with zero remarks or quality exceptions noted!",
            "All 18 pallets of vaccines have been transferred into their automated cold-storage vault safely without a single vial lost or compromised.",
            "Driver Santosh has received his digital unloading discharge slip and is now moving the truck to the overnight parking area.",
            "This has been one of the most remarkable operational recovery experiences we have ever had with any logistics technology partner.",
            "We are truly grateful to the RoadLancer Priority Desk and your personal dedication today.",
            "",
            "We are ready to officially close out this incident ticket.",
            "Rajesh Kumar"
        ]
    },
    # 18. Agent (Index 17)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "CONGRATULATIONS! That is the absolute best possible outcome we could ever hope for when handling a critical cold-chain emergency.",
            "Delivering 18 pallets of high-value vaccines with zero quality exceptions after a major highway mechanical breakdown is a testament to: Your team's professional discipline, Driver Santosh's rapid reporting, and our unified IoT & mobile repair ecosystem.",
            "Let's do a complete final wrap-up and documentation check for your records:",
            "1. Electronic Proof of Delivery (e-POD): #EPOD-2026-BH-9912 is archived on your dashboard with Dr. Arvind Mehta's digital signature and timestamp (19:55 IST).",
            "2. Final Incident Diagnostic Report (IDR): #IDR-2026-NH48-1001 is now marked as `CLOSED - FULLY COMPLIANT` with all audit logs permanently sealed on our blockchain registry.",
            "3. Billing & Wallet Ledger: Supplemental repair charge (INR 4,500) and FASTag toll credit reimbursement (INR 310) are reconciled cleanly against Wallet #WALLET-APEX-09.",
            "4. Vehicle Health Status: MH-04-EK-9912 telematics profile has been updated to reflect new drive belt (Part #TK-9921) and R-404A refrigerant top-up, with next preventative maintenance reminder scheduled for 15,000 km.",
            "I have verified that all documents, invoices, and audit trails are downloadable directly from your portal under `Tickets -> SUP-1001 -> Artifacts`.",
            "Before I mark the ticket status as `resolved`, do you or your executive team need any further customized analytical summaries or custom audit exports for this shipment?",
            "",
            "With utmost appreciation,",
            "Sarah Jenkins | RoadLancer Priority Desk"
        ]
    },
    # 19. Customer (Index 18)
    {
        "role": "user",
        "type": "customer",
        "name": "Rajesh Kumar (Apex Pharma Logistics)",
        "lines": [
            "Hi Sarah,",
            "",
            "No further customized summaries or audit exports are required at this stage. You have covered every conceivable detail with absolute precision and clarity.",
            "I just downloaded the complete `.zip` document bundle from `Tickets -> SUP-1001 -> Artifacts` and forwarded it to our Managing Director and Head of Compliance.",
            "Our Managing Director specifically asked me to convey his personal appreciation to you and the RoadLancer engineering team.",
            "He noted that the way RoadLancer handled this emergency—from remote IoT diagnostics and 22-minute repair dispatch to digital checkpost clearance and automated QA log emails—demonstrates true industry leadership.",
            "As a result of this flawless experience, our management has decided to migrate all 45 of our remaining refrigerated trailers from our legacy tracking provider over to the RoadLancer Supreme IoT Telematics tier starting next month.",
            "Our fleet manager will reach out to your enterprise sales team on Monday morning to initiate the hardware onboarding schedule for the remaining 45 trucks.",
            "For right now, driver Santosh is resting safely at the Bhiwandi driver dormitories, our cargo is secure inside Pfizer's vaults, and our ledger is 100% reconciled.",
            "Please go ahead and officially transition this support ticket status to `resolved` or `closed`.",
            "It has been an absolute pleasure working with you today.",
            "",
            "Best regards and have a wonderful evening,",
            "Rajesh Kumar | Fleet Operations Lead | Apex Pharma Logistics"
        ]
    },
    # 20. Agent (Index 19)
    {
        "role": "admin",
        "type": "agent",
        "name": "Sarah Jenkins (Senior IoT & Emergency Support Specialist)",
        "lines": [
            "Hi Rajesh,",
            "",
            "That is truly heartwarming to read! Knowing that our partnership and technology during today's highway incident earned the trust of your Managing Director to migrate your entire 45-truck refrigerated fleet over to the RoadLancer Supreme IoT tier is the highest compliment our team could ever receive.",
            "I will personally brief our Enterprise Onboarding Lead, Mr. Vikramaditya Rao, first thing on Monday morning so that your fleet manager experiences a VIP, white-glove hardware installation schedule with zero operational downtime for your existing contracts.",
            "To officially close out this support interaction:",
            "- Ticket Number: TICK-1001 (Internal ID: 1001)",
            "- Final Status: `resolved` / `closed`",
            "- Total Conversation Log: 20 comprehensive diagnostic and resolution entries logged with immutable timestamps.",
            "- Quality Score: 100% Cold-Chain Integrity Maintained (2.0°C to 6.3°C throughout).",
            "If you or Santosh ever need immediate assistance during transit on any highway across India, our 24/7 Priority Breakdown Desk is always just one click or phone call away.",
            "I am officially transitioning this ticket to `resolved` in our database right now.",
            "Thank you once again for choosing RoadLancer as your trusted logistics and telematics partner.",
            "Have a peaceful and restful weekend ahead!",
            "",
            "Best regards,",
            "Sarah Jenkins",
            "RoadLancer Support Team",
            "https://roadlancer.com"
        ]
    }
]

async def seed_ticket_1001_replies():
    print("🔌 Connecting to database...")
    if not db.is_connected():
        await db.connect()

    print("🔍 Locating or creating ticket 1001...")
    # Try to find ticket with ticketNumber = TICK-1001 or SUP-1001 or id = 1001
    ticket = await db.support_tickets.find_first(
        where={
            "OR": [
                {"ticketNumber": "TICK-1001"},
                {"ticketNumber": "SUP-1001"},
                {"ticketNumber": "1001"},
                {"id": "1001"},
                {"ticketNumber": {"contains": "1001"}}
            ]
        }
    )

    now = datetime.utcnow()
    # If ticket doesn't exist, create it cleanly with id='1001' and ticketNumber='TICK-1001'
    if not ticket:
        print("⚡ Ticket 1001 not found. Creating TICK-1001 (ID: 1001)...")
        ticket = await db.support_tickets.create(data={
            "id": "1001",
            "ticketNumber": "TICK-1001",
            "senderEmail": "rajesh.k@apexpharma.in",
            "senderName": "Rajesh Kumar (Apex Pharma Logistics)",
            "subject": "[URGENT] Reefer container temperature alarm on NH-48",
            "message": "The refrigerated truck carrying pharmaceutical goods shows a temperature rise above 4°C. Need immediate breakdown assistance near Surat checkpost.\n\nVehicle: MH-04-EK-9912\nCargo: Pfizer Distribution Center Vaccines (INR 42 Lakhs)\nLocation: NH-48 near Surat South Checkpost.",
            "category": "logistics_breakdown",
            "status": "in_progress",
            "priority": "urgent",
            "source": "email",
            "adminNotes": "[ASSIGNED_TO:agent-001|Sarah Jenkins (Support Lead)]\nPriority-1 Breakdown intervention on NH-48. Certified technician dispatched from ColdChain Tech Services.",
            "createdAt": now - timedelta(hours=48),
            "updatedAt": now
        })
        print(f"✅ Created ticket: {ticket.ticketNumber} (ID: {ticket.id})")
    else:
        print(f"✅ Found existing ticket: {ticket.ticketNumber} (ID: {ticket.id})")
        # Ensure subject and attributes reflect the rich reefer conversation if needed
        await db.support_tickets.update(
            where={"id": ticket.id},
            data={
                "senderName": "Rajesh Kumar (Apex Pharma Logistics)",
                "senderEmail": "rajesh.k@apexpharma.in",
                "subject": "[URGENT] Reefer container temperature alarm on NH-48",
                "status": "resolved",
                "priority": "urgent",
                "updatedAt": now
            }
        )

    # Clean any existing replies for this specific ticket so we have exactly our 20 crisp replies
    print(f"🧹 Clearing existing replies for ticket {ticket.ticketNumber} ({ticket.id})...")
    deleted_replies = await db.ticket_replies.delete_many(where={"ticketId": ticket.id})
    print(f"Removed {deleted_replies} old replies.")

    print("🚀 Seeding 20 alternating, multi-line replies for ticket 1001...")
    start_time = now - timedelta(hours=46)

    for i, item in enumerate(REPLIES_DATA):
        # Space out timestamps across the 46-hour window
        reply_time = start_time + timedelta(hours=(i * 2.3) + random.uniform(0.1, 0.4))
        raw_text = "\n".join(item["lines"])
        
        # Format HTML representation with proper paragraph spacing
        html_paragraphs = [f"<p style='margin-bottom: 0.75rem; line-height: 1.6;'>{line}</p>" if line.strip() else "<br/>" for line in item["lines"]]
        body_html = f"<div class='reply-formatted-content'>{''.join(html_paragraphs)}</div>"

        await db.ticket_replies.create(data={
            "ticketId": ticket.id,
            "senderName": item["name"],
            "senderRole": item["role"],  # 'user' vs 'admin'
            "senderType": item["type"],  # 'customer' vs 'agent'
            "message": raw_text,
            "bodyHtml": body_html,
            "createdAt": reply_time
        })
        print(f"  💬 Seeded Reply #{i+1:02d} [{item['type'].upper()}]: {item['name'].split('(')[0].strip()} ({len(item['lines'])} lines)")

    # Final update on ticket updatedAt timestamp to match the 20th reply
    await db.support_tickets.update(
        where={"id": ticket.id},
        data={
            "status": "resolved",
            "updatedAt": now
        }
    )

    print(f"\n🎉 Successfully seeded exactly 20 multi-line alternating replies for ticket {ticket.ticketNumber} (ID: {ticket.id})!")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_ticket_1001_replies())
