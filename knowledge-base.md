# RoadLancer Knowledge Base & Auto-Resolution Guide
*Internal Operational Knowledge Base for AI Auto-Resolution & Support Agents*

---

## 1. Billing, Payments & FASTag Disputes

### Q1.1: FASTag Double Deduction at Toll Plaza
- **Issue**: Shipper or driver reports that toll charges (e.g., ₹4,850 or standard axle toll) were deducted twice from their RoadLancer FASTag / wallet at a checkpost or toll plaza.
- **Auto-Resolution Answer**:
  > "We have verified your FASTag transaction logs. When a double deduction occurs due to toll scanner lag or server timeout, NPCI automatically initiates a chargeback sweep within **5 to 7 business days**. The duplicate amount will be credited directly back to your RoadLancer wallet automatically—no action is needed on your part. If the refund is not reflected after 7 business days, please reply to this ticket with your Vehicle RC copy and Toll Plaza name/receipt number."
- **Auto-Resolve Eligibility**: **YES** (Standard inquiry / dispute).

### Q1.2: Freight Invoice Delay & Settlement Timelines
- **Issue**: Carrier asking when their remaining 30% balance or final freight invoice will be settled after trip completion.
- **Auto-Resolution Answer**:
  > "Final payment settlements are processed within **24 to 48 business hours** after the digital Proof of Delivery (POD) with clear consignee stamp/signature is uploaded and verified on the Shipper Dashboard. If your POD has already been uploaded for over 48 hours, our accounts team is expediting the release to your linked bank account today."
- **Auto-Resolve Eligibility**: **YES**.

### Q1.3: Fuel Advance (70% Advance Credit)
- **Issue**: Driver asking about fuel advance upon pickup.
- **Auto-Resolution Answer**:
  > "Once the shipper confirms loading and generates the e-Way bill on the RoadLancer platform, **70% of the trip freight value** is credited immediately to your RoadLancer Fuel & Toll Wallet. You can use this advance at any partner fuel station across National Highways."
- **Auto-Resolve Eligibility**: **YES**.

---

## 2. KYC & Document Verification

### Q2.1: KYC Status Pending or Approval Time
- **Issue**: Driver or Fleet Owner asking how long RC book, Driving License, National Permit, or GST verification takes.
- **Auto-Resolution Answer**:
  > "Our verification team processes all document submissions (`RC Book`, `Commercial Driving License`, `Aadhaar`, and `GST Certificate`) strictly in chronological order. Typical review times are between **2 to 4 business hours** during working days (9 AM – 7 PM IST). You will receive an automated SMS and WhatsApp notification once your verification status turns to **Verified**."
- **Auto-Resolve Eligibility**: **YES**.

### Q2.2: KYC Rejection Reasons (Blurry Photos / Expired Fitness)
- **Issue**: Driver reports document was rejected during KYC.
- **Auto-Resolution Answer**:
  > "The most common reasons for document rejection are: (1) Blurry or cut-off photos of the commercial RC Book, or (2) Expired Vehicle Fitness Certificate / Insurance. Please navigate to **Driver Dashboard → Document Verification** (`/driver/get-validated`) and re-upload high-resolution, uncropped photos of your updated documents for priority 1-hour re-verification."
- **Auto-Resolve Eligibility**: **YES**.

---

## 3. Shipment Tracking & Telematics

### Q3.1: GPS Tracking Loss or Telematics Signal Disconnect
- **Issue**: Shipper or admin notes GPS signal lost for vehicle on highway or telematics disconnect.
- **Auto-Resolution Answer**:
  > "GPS signal loss on highways often occurs in low-network corridors (such as ghat sections or remote highways) or when the vehicle's OBD telematics device enters sleep mode during driver rest stops. Please instruct the driver to check the OBD device indicator light upon restarting the engine. If the signal does not resume within 30 minutes, our telematics support team will dispatch an SMS check ping to the driver's mobile phone."
- **Auto-Resolve Eligibility**: **YES** (unless marked priority `urgent` / SOS).

### Q3.2: POD (Proof of Delivery) Upload Help
- **Issue**: Driver unable to upload POD photo.
- **Auto-Resolution Answer**:
  > "To upload your Proof of Delivery (POD), go to your **Driver Dashboard**, select the active shipment, and click **Upload POD**. Ensure the photo clearly shows the receiver's stamp, signature, and date of delivery. File size must be under 10 MB (JPG, PNG, or PDF)."
- **Auto-Resolve Eligibility**: **YES**.

---

## 4. Account & Access Issues

### Q4.1: OTP Password Reset Delay or Failure
- **Issue**: User unable to receive OTP or reset password on mobile.
- **Auto-Resolution Answer**:
  > "If you are experiencing delays receiving OTP SMS, please ensure your mobile network signal is strong and check if DND (Do Not Disturb) filters are blocking commercial SMS shortcodes. You can also click **Resend via WhatsApp** on the login screen. If you recently changed your registered mobile number, please email a copy of your commercial Driving License or Aadhaar to `kyc-support@roadlancer.in` to update your registered phone number."
- **Auto-Resolve Eligibility**: **YES**.

### Q4.2: CSV Export or Report Download
- **Issue**: Shipper asking how to export monthly carbon emissions or trip reports to CSV/Excel.
- **Auto-Resolution Answer**:
  > "You can download all monthly trip logs, freight invoices, and carbon emission analytics directly from **Shipper Dashboard → Reports & Analytics**. Click the **Export CSV** button in the top right corner and select your desired date range."
- **Auto-Resolve Eligibility**: **YES**.

---

## 5. Logistics Breakdowns & SOS (Exceptions - Do NOT Auto-Resolve)

### Q5.1: Active Reefer Compressor Failure / Temperature Alarm (SOS)
- **Issue**: Reefer compressor failure, perishable goods/vaccines at risk, active highway breakdown, checkpost detention, or active accident.
- **Auto-Resolution Answer**:
  > *None. EMERGENCY SOS & URGENT BREAKDOWN TICKETS REQUIRE IMMEDIATE HUMAN AGENT INTERVENTION.*
- **Auto-Resolve Eligibility**: **NO** (Must remain `open` and assigned `priority: "urgent"` or `"high"`).
