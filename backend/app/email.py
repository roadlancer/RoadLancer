import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_reply_email(
    to_email: str,
    subject: str,
    html_body: str,
    ticket_number: str,
    sender_name: str = "RoadLancer Support",
):
    """Send a support reply email via Gmail SMTP (fire-and-forget)."""
    smtp_email = os.getenv("SMTP_EMAIL", "")
    smtp_password = os.getenv("SMTP_APP_PASSWORD", "")

    if not smtp_email or not smtp_password:
        print(f"⚠️ [email] SMTP not configured — skipping email to {to_email}")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{sender_name} <{smtp_email}>"
    msg["To"] = to_email
    msg["Subject"] = f"Re: [{ticket_number}] {subject}"
    msg["Reply-To"] = smtp_email
    msg["X-Mailer"] = "RoadLancer-Support"

    plain_text = f"Your support ticket {ticket_number} has been updated.\n\n{subject}\n\nPlease view the full reply in the RoadLancer support portal."
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, to_email, msg.as_string())
        print(f"✅ [email] Reply sent to {to_email} for ticket {ticket_number}")
        return True
    except Exception as e:
        print(f"❌ [email] Failed to send reply to {to_email}: {e}")
        return False
