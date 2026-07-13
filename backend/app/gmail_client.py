"""
Gmail API client for sending and receiving emails.
Uses Google Service Account with Domain-wide Delegation for production.
"""
import os
import base64
import json
import logging
from email.message import EmailMessage
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

_gmail_service = None


def _get_gmail_service():
    """Get or create Gmail API service using service account credentials."""
    global _gmail_service
    if _gmail_service:
        return _gmail_service

    service_account_json = os.getenv("GMAIL_SERVICE_ACCOUNT_JSON", "")
    gmail_user = os.getenv("GMAIL_USER_EMAIL", "support.roadlancer@gmail.com")

    if not service_account_json:
        logger.warning("GMAIL_SERVICE_ACCOUNT_JSON not configured")
        return None

    try:
        creds_info = json.loads(service_account_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES
        )
        # Impersonate the Gmail user (requires Domain-wide Delegation)
        delegated_credentials = credentials.with_subject(gmail_user)
        _gmail_service = build("gmail", "v1", credentials=delegated_credentials)
        logger.info(f"Gmail API service created for {gmail_user}")
        return _gmail_service
    except Exception as e:
        logger.error(f"Failed to create Gmail service: {e}")
        return None


def send_email_via_gmail(
    to_email: str,
    subject: str,
    html_body: str,
    ticket_number: str,
    sender_name: str = "RoadLancer Support",
) -> bool:
    """Send an email using Gmail API."""
    gmail_user = os.getenv("GMAIL_USER_EMAIL", "support.roadlancer@gmail.com")
    service = _get_gmail_service()

    if not service:
        logger.warning("Gmail service not available, falling back to Resend")
        return False

    try:
        message = EmailMessage()
        message.set_content(html_body, subtype="html")
        message["to"] = to_email
        message["from"] = f"{sender_name} <{gmail_user}>"
        message["subject"] = f"Re: [{ticket_number}] {subject}"
        message["reply-to"] = gmail_user

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        result = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message})
            .execute()
        )

        logger.info(f"Email sent to {to_email} for ticket {ticket_number}, id: {result.get('id')}")
        return True

    except HttpError as e:
        logger.error(f"Gmail API error sending to {to_email}: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def fetch_email_by_id(email_id: str) -> Optional[dict]:
    """Fetch a specific email by ID from Gmail."""
    service = _get_gmail_service()
    if not service:
        return None

    try:
        message = (
            service.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )

        headers = {h["name"].lower(): h["value"] for h in message.get("payload", {}).get("headers", [])}

        body = ""
        payload = message.get("payload", {})
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break
                elif part.get("mimeType") == "text/html" and not body:
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
        elif payload.get("body", {}).get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

        return {
            "id": message.get("id"),
            "from": headers.get("from", ""),
            "to": headers.get("to", ""),
            "subject": headers.get("subject", "No Subject"),
            "body": body,
            "snippet": message.get("snippet", ""),
        }

    except Exception as e:
        logger.error(f"Failed to fetch email {email_id}: {e}")
        return None


def list_recent_emails(max_results: int = 10) -> list:
    """List recent emails from Gmail inbox."""
    service = _get_gmail_service()
    if not service:
        return []

    try:
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
            .execute()
        )

        messages = results.get("messages", [])
        emails = []
        for msg in messages:
            email_data = fetch_email_by_id(msg["id"])
            if email_data:
                emails.append(email_data)

        return emails

    except Exception as e:
        logger.error(f"Failed to list emails: {e}")
        return []


def mark_email_as_read(email_id: str) -> bool:
    """Mark an email as read by removing UNREAD label."""
    service = _get_gmail_service()
    if not service:
        return False

    try:
        service.users().messages().modify(
            userId="me",
            id=email_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to mark email {email_id} as read: {e}")
        return False
