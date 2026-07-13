"""
Gmail API client for sending and receiving emails.
Supports both token-based auth (development) and service account (production).
"""
import os
import base64
import json
import logging
from email.message import EmailMessage
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

_gmail_service = None


def _get_gmail_service():
    """Get or create Gmail API service using token or service account."""
    global _gmail_service
    if _gmail_service:
        return _gmail_service

    gmail_user = os.getenv("GMAIL_USER_EMAIL", "support.roadlancer@gmail.com")

    # Try token-based auth first (simpler, works with refresh token)
    token_json = os.getenv("GMAIL_TOKEN_JSON", "")
    if token_json:
        try:
            token_data = json.loads(token_json)
            creds = Credentials(
                token=token_data.get("token", ""),
                refresh_token=token_data.get("refresh_token", ""),
                token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=token_data.get("client_id", ""),
                client_secret=token_data.get("client_secret", ""),
                scopes=token_data.get("scopes", []),
            )
            if creds.expired or not creds.valid:
                creds.refresh(Request())
            _gmail_service = build("gmail", "v1", credentials=creds)
            logger.info(f"Gmail API service created (token-based) for {gmail_user}")
            return _gmail_service
        except Exception as e:
            logger.error(f"Failed to create Gmail service from token: {e}")

    # Try service account auth
    service_account_json = os.getenv("GMAIL_SERVICE_ACCOUNT_JSON", "")
    if service_account_json:
        try:
            from google.oauth2 import service_account

            SCOPES = [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.modify",
            ]
            creds_info = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                creds_info, scopes=SCOPES
            )
            delegated_credentials = credentials.with_subject(gmail_user)
            _gmail_service = build("gmail", "v1", credentials=delegated_credentials)
            logger.info(f"Gmail API service created (service account) for {gmail_user}")
            return _gmail_service
        except Exception as e:
            logger.error(f"Failed to create Gmail service from service account: {e}")

    logger.warning("Gmail API not configured (no GMAIL_TOKEN_JSON or GMAIL_SERVICE_ACCOUNT_JSON)")
    return None


def send_email_via_gmail(
    to_email: str,
    subject: str,
    html_body: str,
    ticket_number: str,
    sender_name: str = "RoadLancer Support",
    thread_id: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
) -> bool:
    """Send an email using Gmail API. Supports threading via thread_id and In-Reply-To."""
    gmail_user = os.getenv("GMAIL_USER_EMAIL", "support.roadlancer@gmail.com")
    service = _get_gmail_service()

    if not service:
        return False

    try:
        message = EmailMessage()
        message.set_content(html_body, subtype="html")
        message["to"] = to_email
        message["from"] = f"{sender_name} <{gmail_user}>"
        message["subject"] = f"Re: [{ticket_number}] {subject}"
        message["reply-to"] = gmail_user

        if in_reply_to:
            message["In-Reply-To"] = in_reply_to
        if references:
            message["References"] = references

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        body = {"raw": raw_message}
        if thread_id:
            body["threadId"] = thread_id

        result = (
            service.users()
            .messages()
            .send(userId="me", body=body)
            .execute()
        )

        logger.info(f"Email sent to {to_email} for ticket {ticket_number}, id: {result.get('id')}, thread: {thread_id or 'new'}")
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

        headers = {
            h["name"].lower(): h["value"]
            for h in message.get("payload", {}).get("headers", [])
        }

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
