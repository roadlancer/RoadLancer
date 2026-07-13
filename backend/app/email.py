"""
Email sending module — tries Gmail API first, falls back to Resend API.
"""
import os
import httpx
import logging

logger = logging.getLogger(__name__)


def send_reply_email(
    to_email: str,
    subject: str,
    html_body: str,
    ticket_number: str,
    sender_name: str = "RoadLancer Support",
) -> bool:
    """Send a support reply email. Tries Gmail API first, falls back to Resend."""
    from app.gmail_client import send_email_via_gmail

    # Try Gmail API first
    gmail_user = os.getenv("GMAIL_USER_EMAIL", "")
    token_json = os.getenv("GMAIL_TOKEN_JSON", "")
    service_account_json = os.getenv("GMAIL_SERVICE_ACCOUNT_JSON", "")

    if gmail_user and (token_json or service_account_json):
        result = send_email_via_gmail(to_email, subject, html_body, ticket_number, sender_name)
        if result:
            return True
        logger.warning("Gmail API failed, falling back to Resend")

    # Fallback to Resend API
    return _send_via_resend(to_email, subject, html_body, ticket_number, sender_name)


def _send_via_resend(
    to_email: str,
    subject: str,
    html_body: str,
    ticket_number: str,
    sender_name: str = "RoadLancer Support",
) -> bool:
    """Send email via Resend API (HTTPS)."""
    resend_api_key = os.getenv("RESEND_API_KEY", "")
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    verified_email = os.getenv("RESEND_VERIFIED_EMAIL", "support.roadlancer@gmail.com")

    if not resend_api_key:
        logger.warning("RESEND_API_KEY not configured, skipping email")
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
        import asyncio

        async def _send():
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {resend_api_key}",
                        "Content-Type": "application/json",
                    },
                )
                return resp.status_code in (200, 201), resp.status_code, resp.text

        loop = asyncio.new_event_loop()
        ok, status, text = loop.run_until_complete(_send())
        loop.close()

        if ok:
            logger.info(f"Email sent to {actual_to} for ticket {ticket_number} via Resend")
            return True
        else:
            logger.error(f"Resend API error ({status}): {text}")
            return False

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
