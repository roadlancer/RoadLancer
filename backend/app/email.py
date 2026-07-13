import os
import httpx


async def send_reply_email(
    to_email: str,
    subject: str,
    html_body: str,
    ticket_number: str,
    sender_name: str = "RoadLancer Support",
):
    """Send a support reply email via Resend API (HTTPS)."""
    resend_api_key = os.getenv("RESEND_API_KEY", "")
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    verified_email = os.getenv("RESEND_VERIFIED_EMAIL", "support.roadlancer@gmail.com")

    if not resend_api_key:
        print(f"⚠️ [email] RESEND_API_KEY not configured — skipping email to {to_email}", flush=True)
        return False

    actual_to = to_email
    test_mode = False
    if from_email == "onboarding@resend.dev" and to_email.lower() != verified_email.lower():
        actual_to = verified_email
        test_mode = True

    msg_subject = f"Re: [{ticket_number}] {subject}"
    plain_text = f"Your support ticket {ticket_number} has been updated.\n\n{subject}\n\nPlease view the full reply in the RoadLancer support portal."
    if test_mode:
        plain_text = f"[TEST MODE] Original recipient: {to_email}\n\n{plain_text}"

    payload = {
        "from": f"{sender_name} <{from_email}>",
        "to": [actual_to],
        "subject": msg_subject,
        "text": plain_text,
        "html": html_body,
        "reply_to": from_email,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json",
                },
            )
            if resp.status_code in (200, 201):
                print(f"✅ [email] Reply sent to {actual_to} for ticket {ticket_number} via Resend", flush=True)
                return True
            else:
                print(f"❌ [email] Resend API error ({resp.status_code}): {resp.text}", flush=True)
                return False
    except Exception as e:
        print(f"❌ [email] Failed to send reply to {to_email}: {e}", flush=True)
        return False
