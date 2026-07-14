import os
import random
import time
import traceback
import uuid
import asyncio
import hmac
import hashlib
import base64
import httpx
import json
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from app.database import db
from app.routes.auth import get_current_user
from app.routes.admin import get_admin_user
from app.email import send_reply_email

router = APIRouter()


class InboundEmailRequest(BaseModel):
    from_email: str = Field(max_length=255)
    from_name: Optional[str] = Field(default=None, max_length=100)
    subject: str = Field(max_length=200)
    body: str = Field(max_length=5000)
    category: Optional[str] = Field(default="general", max_length=50)
    priority: Optional[str] = Field(default="normal", max_length=20)
    source: Optional[str] = Field(default="email", max_length=20)
    secret: Optional[str] = None
    gmail_thread_id: Optional[str] = None
    gmail_message_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: Optional[str] = None


class CreateTicketRequest(BaseModel):
    subject: str = Field(max_length=200)
    message: str = Field(max_length=5000)
    category: Optional[str] = Field(default="general", max_length=50)
    priority: Optional[str] = Field(default="normal", max_length=20)
    source: Optional[str] = Field(default="web", max_length=20)


class UpdateTicketStatusRequest(BaseModel):
    status: Optional[str] = Field(default=None, max_length=20)
    category: Optional[str] = Field(default=None, max_length=50)
    admin_notes: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = Field(default=None, max_length=20)


class CreateTicketReplyRequest(BaseModel):
    message: str = Field(max_length=5000)
    sender_name: Optional[str] = Field(default=None, max_length=100)


class PolishReplyRequest(BaseModel):
    draft: str = Field(max_length=5000)
    message: Optional[str] = Field(default=None, max_length=5000)


class PolishReplyResponse(BaseModel):
    polished: str
    success: bool = True
    source: str = "FastAPI Backend"


async def ensure_ticket_replies_table():
    try:
        await db.query_raw("""
            CREATE TABLE IF NOT EXISTS ticket_replies (
                id TEXT PRIMARY KEY,
                ticket_id TEXT NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
                sender_name TEXT NOT NULL,
                sender_role TEXT NOT NULL,
                sender_type TEXT NOT NULL DEFAULT 'agent',
                message TEXT NOT NULL,
                created_at TIMESTAMP(3) WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        await db.query_raw("ALTER TABLE ticket_replies ADD COLUMN IF NOT EXISTS sender_type TEXT NOT NULL DEFAULT 'agent';")
        # Add email threading columns if they don't exist
        await db.query_raw('ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS "in_reply_to" TEXT;')
        await db.query_raw('ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS "references" TEXT;')
    except Exception:
        pass


async def fetch_ticket_replies(ticket_id: str) -> list:
    await ensure_ticket_replies_table()
    try:
        replies = await db.query_raw(
            'SELECT id, ticket_id as "ticketId", sender_name as "senderName", sender_role as "senderRole", sender_type as "senderType", message, created_at as "createdAt" FROM ticket_replies WHERE ticket_id = $1 ORDER BY created_at ASC',
            ticket_id,
        )
        return replies or []
    except Exception:
        return []


def ticket_to_dict(t, user_map=None, replies=None) -> dict:
    user_info = None
    if t.userId and user_map and t.userId in user_map:
        u = user_map[t.userId]
        role_val = u.role.value if hasattr(u.role, "value") else u.role
        user_info = {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": role_val,
            "phone": u.phone,
        }

    formatted_replies = []
    if replies:
        for r in replies:
            get_val = lambda obj, k, default=None: obj.get(k, default) if isinstance(obj, dict) else getattr(obj, k, default)
            created_dt = get_val(r, "createdAt") or get_val(r, "created_at")
            role_val = get_val(r, "senderRole") or get_val(r, "sender_role")
            type_val = get_val(r, "senderType") or get_val(r, "sender_type") or ("agent" if role_val == "admin" else "customer")
            formatted_replies.append({
                "id": get_val(r, "id"),
                "ticket_id": get_val(r, "ticketId") or get_val(r, "ticket_id"),
                "sender_name": get_val(r, "senderName") or get_val(r, "sender_name"),
                "sender_role": role_val,
                "sender_type": type_val,
                "message": get_val(r, "message"),
                "created_at": (created_dt if isinstance(created_dt, str) else created_dt.isoformat()) if created_dt else None,
            })

    return {
        "id": t.id,
        "ticket_number": t.ticketNumber,
        "sender_email": t.senderEmail,
        "sender_name": t.senderName,
        "subject": t.subject,
        "message": t.message,
        "category": getattr(t, "category", "general") or "general",
        "status": t.status,
        "priority": t.priority,
        "source": t.source,
        "user_id": t.userId,
        "user": user_info,
        "admin_notes": t.adminNotes,
        "replies": formatted_replies,
        "created_at": (t.createdAt if isinstance(t.createdAt, str) else t.createdAt.isoformat()) if t.createdAt else None,
        "updated_at": (t.updatedAt if isinstance(t.updatedAt, str) else t.updatedAt.isoformat()) if t.updatedAt else None,
    }


async def generate_unique_ticket_number() -> str:
    # Generate TICK-XXXX where XXXX is 4 digits
    if not hasattr(db, "support_tickets"):
        raise HTTPException(
            status_code=500,
            detail="Prisma client attribute 'support_tickets' missing. Please run 'python -m prisma generate' inside the backend folder and restart your FastAPI server.",
        )
    for _ in range(10):
        num = random.randint(1000, 9999)
        ticket_num = f"TICK-{num}"
        try:
            existing = await db.support_tickets.find_unique(where={"ticketNumber": ticket_num})
            if not existing:
                return ticket_num
        except Exception as e:
            print(f"❌ [generate_unique_ticket_number] Error on {ticket_num}: {e}")
            traceback.print_exc()
            err_msg = str(e)
            if "relation \"support_tickets\" does not exist" in err_msg or "table \"support_tickets\" does not exist" in err_msg.lower():
                raise HTTPException(
                    status_code=500,
                    detail="Table 'support_tickets' does not exist in PostgreSQL. Please run 'npx prisma db push --schema=prisma/schema.prisma' and 'python -m prisma generate' inside the backend directory.",
                )
            raise e
    # Fallback if 4 digits collide
    return f"TICK-{int(time.time()) % 100000}"
async def classify_ticket_background(ticket_id: str, subject: str, message: str, sender_name: str = ""):
    """
    Non-blocking background task to enqueue ticket classification & auto-resolution into the pg-boss queue.
    Ensures a single unified flow: Webhook -> pg-boss Queue -> AI Worker (Bun queue.ts).
    If auth-server HTTP API is unreachable, directly inserts the job into the pgboss.job table in PostgreSQL.
    """
    try:
        try:
            await db.support_tickets.update(
                where={"id": ticket_id},
                data={"status": "processing"}
            )
        except Exception as st_err:
            print(f"⚠️ [classify_ticket_background] Could not set processing state: {st_err}")

        # Attempt 1: Enqueue via Bun auth-server API
        async with httpx.AsyncClient(timeout=4.0) as client:
            try:
                res = await client.post(
                    "http://localhost:3000/api/auth/ai/classify",
                    json={
                        "ticketId": ticket_id,
                        "subject": subject,
                        "message": message,
                        "senderName": sender_name,
                        "background": True,
                    }
                )
                if res.status_code in (200, 202):
                    print(f"📦 [classify_ticket_background] Successfully enqueued ticket {ticket_id} to pg-boss queue via auth-server API.")
                    return
            except Exception as queue_err:
                print(f"⚠️ [classify_ticket_background] auth-server HTTP API unreachable ({queue_err}). Enqueuing directly into PostgreSQL pgboss.job table.")

        # Attempt 2: If auth-server HTTP API is unreachable, enqueue directly into PostgreSQL pgboss.job table
        try:
            job_id = str(uuid.uuid4())
            await db.query_raw(
                """
                INSERT INTO pgboss.job (
                    id, name, priority, data, state, retry_limit, retry_count, retry_delay, retry_backoff, start_after, created_on
                ) VALUES (
                    $1::uuid, 'classify-ticket', 0, $2::jsonb, 'created'::pgboss.job_state, 3, 0, 5000, true, NOW(), NOW()
                )
                """,
                job_id,
                json.dumps({"ticketId": ticket_id, "subject": subject, "message": message, "senderName": sender_name}),
            )
            print(f"📦 [classify_ticket_background] Successfully enqueued ticket {ticket_id} directly into pgboss.job table (Job ID: {job_id}).")
        except Exception as db_err:
            print(f"❌ [classify_ticket_background] Failed to enqueue directly into pgboss.job: {db_err}")
            try:
                await db.support_tickets.update(where={"id": ticket_id}, data={"status": "open"})
            except Exception:
                pass

    except Exception as exc:
        print(f"❌ [classify_ticket_background] Uncaught exception during queue dispatch for ticket {ticket_id}: {exc}")
        try:
            await db.support_tickets.update(where={"id": ticket_id}, data={"status": "open"})
        except Exception:
            pass


@router.post("/inbound-email")
async def simulate_inbound_email(
    req: InboundEmailRequest,
    x_webhook_secret: Optional[str] = Header(None, alias="x-webhook-secret"),
    authorization: Optional[str] = Header(None),
):
    """
    Webhook endpoint simulating an inbound email parser (like SendGrid/Mailgun/Postmark).
    Receives email payload, links to user account if email matches, and creates support ticket.
    Requires a valid webhook secret matching SUPPORT_WEBHOOK_SECRET loaded from .env.
    """
    expected_secret = os.getenv("SUPPORT_WEBHOOK_SECRET", "roadlancer-webhook-secret-2026")
    provided_secret = req.secret or x_webhook_secret
    if authorization and authorization.startswith("Bearer "):
        provided_secret = provided_secret or authorization.replace("Bearer ", "").strip()

    if provided_secret != expected_secret:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid or missing webhook secret ('x-webhook-secret' header or 'secret' field)",
        )

    if not req.from_email or not req.subject or not req.body:
        raise HTTPException(
            status_code=400,
            detail="from_email, subject, and body are required",
        )

    if not hasattr(db, "support_tickets"):
        raise HTTPException(
            status_code=500,
            detail="Prisma client attribute 'support_tickets' missing. Please run 'python -m prisma generate' inside the backend folder and restart your FastAPI server.",
        )

    # Ensure threading columns exist (migration)
    await ensure_ticket_replies_table()

    # Validate sender email exists in the application
    user = await db.user.find_unique(where={"email": req.from_email.lower()})
    if not user:
        raise HTTPException(
            status_code=403,
            detail="Email address not registered in the application. Only emails from registered users are accepted.",
        )

    last_exc = None
    for _attempt in range(3):
        try:
            user_id = user.id
            sender_name = req.from_name or user.name

            ticket_number = await generate_unique_ticket_number()

            ticket = await db.support_tickets.create(
                data={
                    "ticketNumber": ticket_number,
                    "senderEmail": req.from_email.lower(),
                    "senderName": sender_name,
                    "subject": req.subject,
                    "message": req.body,
                    "category": req.category or "general",
                    "priority": req.priority or "normal",
                    "source": req.source or "email",
                    "userId": user_id,
                    "status": "new",
                    "gmailThreadId": req.gmail_thread_id,
                    "gmailMessageId": req.gmail_message_id,
                    "inReplyTo": req.in_reply_to,
                    "references": req.references,
                }
            )
            asyncio.create_task(classify_ticket_background(ticket.id, req.subject, req.body, sender_name))
            break
        except Exception as e:
            last_exc = e
            err_msg = str(e)
            # Fatal schema errors — don't retry
            if "relation \"support_tickets\" does not exist" in err_msg or "table \"support_tickets\" does not exist" in err_msg.lower():
                raise HTTPException(
                    status_code=500,
                    detail="Table 'support_tickets' does not exist in PostgreSQL. Please run 'npx prisma db push --schema=prisma/schema.prisma' and 'python -m prisma generate' inside the backend directory.",
                )
            # Retry on transient Prisma engine errors (AttributeError from malformed error response)
            if isinstance(e, AttributeError) and _attempt < 2:
                print(f"⚠️ [simulate_inbound_email] Transient Prisma error (attempt {_attempt + 1}/3): {e}")
                await asyncio.sleep(0.5 * (_attempt + 1))
                continue
            print(f"❌ [simulate_inbound_email] Exception during ticket creation: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Database error while creating ticket: {err_msg} | {traceback.format_exc().splitlines()[-1] if traceback.format_exc() else ''}")
    else:
        raise HTTPException(status_code=500, detail=f"Database error after retries: {last_exc}")

    user_map = {user_id: user} if user else {}
    return {
        "success": True,
        "ticket_number": ticket_number,
        "ticket": ticket_to_dict(ticket, user_map),
        "message": f"Inbound email from {req.from_email} converted to ticket #{ticket_number}",
    }


def _verify_resend_signature(payload: bytes, headers: dict, secret: str) -> bool:
    """Verify Resend webhook HMAC-SHA256 signature (Svix format)."""
    svix_id = headers.get("svix-id", "")
    svix_timestamp = headers.get("svix-timestamp", "")
    svix_signature = headers.get("svix-signature", "")

    if not all([svix_id, svix_timestamp, svix_signature]):
        return False

    to_sign = f"{svix_id}.{svix_timestamp}.{payload.decode('utf-8', errors='replace')}"
    secret_bytes = secret.encode("utf-8")
    expected = hmac.new(secret_bytes, to_sign.encode("utf-8"), hashlib.sha256).digest()
    expected_b64 = base64.b64encode(expected).decode("utf-8")

    for sig_part in svix_signature.split(" "):
        if hmac.compare_digest(f"v1,{expected_b64}", sig_part):
            return True
    return False


@router.post("/webhook/resend")
async def handle_resend_webhook(request: Request):
    """
    Webhook endpoint for Resend inbound emails.
    Receives email.received events, fetches full email content, and creates support ticket.
    """
    webhook_secret = os.getenv("RESEND_WEBHOOK_SECRET", "")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="RESEND_WEBHOOK_SECRET not configured")

    raw_body = await request.body()

    if not _verify_resend_signature(raw_body, dict(request.headers), webhook_secret):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    try:
        event = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = event.get("type")
    if event_type != "email.received":
        return {"received": True, "ignored": True, "type": event_type}

    email_id = event.get("data", {}).get("email_id")
    if not email_id:
        raise HTTPException(status_code=400, detail="Missing email_id in webhook data")

    resend_api_key = os.getenv("RESEND_API_KEY", "")
    if not resend_api_key:
        raise HTTPException(status_code=500, detail="RESEND_API_KEY not configured")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://api.resend.com/emails/{email_id}",
                headers={"Authorization": f"Bearer {resend_api_key}"},
            )
            if resp.status_code != 200:
                print(f"❌ [resend-webhook] Failed to fetch email {email_id}: {resp.status_code} {resp.text}")
                raise HTTPException(status_code=502, detail=f"Failed to fetch email from Resend: {resp.status_code}")
            email_data = resp.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout fetching email from Resend")

    from_email = email_data.get("from", "")
    subject = email_data.get("subject", "No Subject")
    text_body = email_data.get("text", "")
    html_body = email_data.get("html", "")
    body = text_body or html_body or ""

    if not from_email:
        raise HTTPException(status_code=400, detail="Missing sender email")

    # Ensure threading columns exist (migration)
    await ensure_ticket_replies_table()

    # Validate sender email exists in the application
    user = await db.user.find_unique(where={"email": from_email.lower()})
    if not user:
        print(f"⚠️ [resend-webhook] Email {from_email} not registered in application, skipping ticket creation")
        return {"received": True, "ignored": True, "reason": "email not registered"}

    user_id = user.id
    sender_name = user.name or from_email.split("@")[0]

    last_exc = None
    for _attempt in range(3):
        try:
            ticket_number = await generate_unique_ticket_number()
            ticket = await db.support_tickets.create(
                data={
                    "ticketNumber": ticket_number,
                    "senderEmail": from_email.lower(),
                    "senderName": sender_name,
                    "subject": subject[:200],
                    "message": body[:5000],
                    "category": "general",
                    "priority": "normal",
                    "source": "email",
                    "userId": user_id,
                    "status": "new",
                }
            )
            asyncio.create_task(classify_ticket_background(ticket.id, subject[:200], body[:5000], sender_name))
            break
        except Exception as e:
            last_exc = e
            err_msg = str(e)
            if "relation \"support_tickets\" does not exist" in err_msg or "table \"support_tickets\" does not exist" in err_msg.lower():
                raise HTTPException(status_code=500, detail="Table 'support_tickets' does not exist")
            if isinstance(e, AttributeError) and _attempt < 2:
                print(f"⚠️ [resend-webhook] Transient Prisma error (attempt {_attempt + 1}/3): {e}")
                await asyncio.sleep(0.5 * (_attempt + 1))
                continue
            print(f"❌ [resend-webhook] Exception during ticket creation: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Database error: {err_msg}")
    else:
        raise HTTPException(status_code=500, detail=f"Database error after retries: {last_exc}")

    user_map = {user_id: user} if user else {}
    print(f"✅ [resend-webhook] Ticket #{ticket_number} created from email by {from_email}")
    return {
        "success": True,
        "ticket_number": ticket_number,
        "ticket": ticket_to_dict(ticket, user_map),
        "message": f"Inbound email from {from_email} converted to ticket #{ticket_number}",
    }


@router.post("/tickets")
async def create_web_ticket(
    req: CreateTicketRequest,
    user: dict = Depends(get_current_user),
):
    """
    Create a support ticket directly from the web interface.
    """
    ticket_number = await generate_unique_ticket_number()

    ticket = await db.support_tickets.create(
        data={
            "ticketNumber": ticket_number,
            "senderEmail": user["email"].lower(),
            "senderName": user.get("name") or user["email"],
            "subject": req.subject,
            "message": req.message,
            "category": req.category or "general",
            "priority": req.priority or "normal",
            "source": req.source or "web",
            "userId": user["id"],
            "status": "new",
        }
    )

    asyncio.create_task(classify_ticket_background(ticket.id, req.subject, req.message, user.get("name") or user["email"]))

    # Fetch full user object for dict conversion
    db_user = await db.user.find_unique(where={"id": user["id"]})
    user_map = {user["id"]: db_user} if db_user else {}
    return ticket_to_dict(ticket, user_map)


@router.post("/tickets/{ticket_id}/classify")
async def trigger_ticket_classification(
    ticket_id: str,
    background: bool = True,
    user: dict = Depends(get_current_user),
):
    """
    Trigger automatic AI ticket classification for an existing ticket using Gemini.
    Runs in non-blocking background fashion by default.
    """
    ticket = await db.support_tickets.find_unique(where={"id": ticket_id})
    if not ticket:
        # Also try by ticketNumber
        ticket = await db.support_tickets.find_unique(where={"ticketNumber": ticket_id})
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

    if background:
        asyncio.create_task(classify_ticket_background(ticket.id, ticket.subject, ticket.message, ticket.senderName or ""))
        return {"success": True, "message": f"Non-blocking classification triggered for ticket #{ticket.ticketNumber}"}
    else:
        await classify_ticket_background(ticket.id, ticket.subject, ticket.message, ticket.senderName or "")
        updated_ticket = await db.support_tickets.find_unique(where={"id": ticket.id})
        return {"success": True, "ticket": ticket_to_dict(updated_ticket)}



def sort_tickets_list(
    tickets: list,
    sort_by: Optional[str] = "newest",
    sort_field: Optional[str] = None,
    sort_order: Optional[str] = "desc",
) -> list:
    """Sort tickets. If sort_field is provided (from TanStack Table column clicks),
    it takes priority over the legacy sort_by dropdown."""
    from datetime import datetime

    def get_timestamp(t):
        val = getattr(t, "createdAt", None)
        if isinstance(val, datetime):
            return val.timestamp() if hasattr(val, "timestamp") else 0
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00")).timestamp()
            except Exception:
                return 0
        return 0

    priority_map = {"urgent": 4, "high": 3, "normal": 2, "low": 1}
    status_map = {"open": 4, "in_progress": 3, "resolved": 2, "closed": 1}

    # --- Per-column sorting (TanStack Table) takes priority ---
    if sort_field:
        is_desc = sort_order == "desc"

        field_to_attr = {
            "ticket_number": "ticketNumber",
            "sender_email": "senderEmail",
            "subject": "subject",
            "source": "source",
            "priority": None,   # weighted
            "status": None,     # weighted
            "created_at": None, # timestamp
        }

        if sort_field == "priority":
            tickets.sort(
                key=lambda t: (
                    priority_map.get(getattr(t, "priority", "normal") or "normal", 0),
                    get_timestamp(t),
                ),
                reverse=is_desc,
            )
        elif sort_field == "status":
            tickets.sort(
                key=lambda t: (
                    status_map.get(getattr(t, "status", "open") or "open", 0),
                    get_timestamp(t),
                ),
                reverse=is_desc,
            )
        elif sort_field == "created_at":
            tickets.sort(key=lambda t: get_timestamp(t), reverse=is_desc)
        elif sort_field in field_to_attr:
            attr = field_to_attr[sort_field]
            tickets.sort(
                key=lambda t: (getattr(t, attr, "") or "").lower(),
                reverse=is_desc,
            )
        else:
            # Unknown field — fall back to newest
            tickets.sort(key=lambda t: get_timestamp(t), reverse=True)
        return tickets

    # --- Legacy sort_by dropdown ---
    if sort_by == "oldest":
        tickets.sort(key=lambda t: get_timestamp(t), reverse=False)
    elif sort_by == "priority":
        tickets.sort(key=lambda t: (priority_map.get(getattr(t, "priority", "normal") or "normal", 0), get_timestamp(t)), reverse=True)
    elif sort_by == "status":
        tickets.sort(key=lambda t: (status_map.get(getattr(t, "status", "open") or "open", 0), get_timestamp(t)), reverse=True)
    else:
        # Default: newest first
        tickets.sort(key=lambda t: get_timestamp(t), reverse=True)
    return tickets


@router.get("/tickets/my")
async def get_my_tickets(
    status: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "newest",
    sort_field: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    user: dict = Depends(get_current_user),
):
    """
    List all support tickets submitted by or linked to the current logged-in user.
    """
    tickets = await db.support_tickets.find_many(
        order={"createdAt": "desc"},
    )
    # Filter in memory since Prisma Python can be picky with OR conditions
    my_tickets = [
        t for t in tickets
        if t.userId == user["id"] or (t.senderEmail and t.senderEmail.lower() == user["email"].lower())
    ]

    if status and status in ("new", "processing", "open", "in_progress", "resolved", "closed"):
        my_tickets = [t for t in my_tickets if t.status == status]
    if source and source in ("email", "web", "profile_edit"):
        my_tickets = [t for t in my_tickets if t.source == source]
    if search:
        search_lower = search.lower()
        my_tickets = [
            t for t in my_tickets
            if search_lower in (t.ticketNumber or "").lower()
            or search_lower in (t.subject or "").lower()
            or search_lower in (t.message or "").lower()
        ]

    my_tickets = sort_tickets_list(my_tickets, sort_by, sort_field, sort_order)

    db_user = await db.user.find_unique(where={"id": user["id"]})
    user_map = {user["id"]: db_user} if db_user else {}

    await ensure_ticket_replies_table()
    try:
        all_replies = await db.query_raw('SELECT id, ticket_id as "ticketId", sender_name as "senderName", sender_role as "senderRole", sender_type as "senderType", message, created_at as "createdAt" FROM ticket_replies ORDER BY created_at ASC')
    except Exception:
        all_replies = []
    reply_map = {}
    if all_replies:
        for r in all_replies:
            tid = r.get("ticketId") or r.get("ticket_id")
            if tid not in reply_map:
                reply_map[tid] = []
            reply_map[tid].append(r)

    return [ticket_to_dict(t, user_map, reply_map.get(t.id)) for t in my_tickets]


@router.get("/admin/list")
async def admin_list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "newest",
    sort_field: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    show_ai_resolved: Optional[bool] = False,
    admin: dict = Depends(get_admin_user),
):
    """
    Admin endpoint to list all support tickets across all users and sources.
    Supreme admins see all tickets. Regular agents see only tickets assigned to them.
    Tickets currently being processed by AI (status: 'processing') are hidden unless explicitly requested.
    Once AI finishes auto-resolving, tickets are fully visible under 'resolved'.
    """
    tickets = await db.support_tickets.find_many()

    user = await db.user.find_unique(where={"id": admin["id"]})
    is_supreme = getattr(user, "isSupreme", False) if user else False

    if not is_supreme:
        assignee_tag = f"[ASSIGNED_TO:{admin['id']}|"
        tickets = [
            t for t in tickets
            if (t.adminNotes and assignee_tag in (t.adminNotes or ""))
            or ("[ASSIGNED_TO:" not in (t.adminNotes or ""))
        ]

    if status and status in ("new", "processing", "open", "in_progress", "resolved", "closed"):
        tickets = [t for t in tickets if t.status == status]

    if priority and priority in ("low", "normal", "high", "urgent"):
        tickets = [t for t in tickets if t.priority == priority]

    if source and source in ("email", "web", "profile_edit"):
        tickets = [t for t in tickets if t.source == source]

    if search:
        search_lower = search.lower()
        tickets = [
            t for t in tickets
            if search_lower in (t.ticketNumber or "").lower()
            or search_lower in (t.senderEmail or "").lower()
            or search_lower in (t.senderName or "").lower()
            or search_lower in (t.subject or "").lower()
            or search_lower in (t.message or "").lower()
        ]

    tickets = sort_tickets_list(tickets, sort_by, sort_field, sort_order)

    users = await db.user.find_many()
    user_map = {u.id: u for u in users}

    await ensure_ticket_replies_table()
    try:
        all_replies = await db.query_raw('SELECT id, ticket_id as "ticketId", sender_name as "senderName", sender_role as "senderRole", sender_type as "senderType", message, created_at as "createdAt" FROM ticket_replies ORDER BY created_at ASC')
    except Exception:
        all_replies = []
    reply_map = {}
    if all_replies:
        for r in all_replies:
            tid = r.get("ticketId") or r.get("ticket_id")
            if tid not in reply_map:
                reply_map[tid] = []
            reply_map[tid].append(r)

    return [ticket_to_dict(t, user_map, reply_map.get(t.id)) for t in tickets]


@router.get("/admin/count")
async def admin_ticket_counts(
    show_ai_resolved: Optional[bool] = False,
    admin: dict = Depends(get_admin_user),
):
    """
    Admin endpoint returning KPI counts for support tickets.
    Supreme admins see all tickets. Regular agents see only tickets assigned to them.
    """
    all_tickets = await db.support_tickets.find_many()

    user = await db.user.find_unique(where={"id": admin["id"]})
    is_supreme = getattr(user, "isSupreme", False) if user else False

    if not is_supreme:
        assignee_tag = f"[ASSIGNED_TO:{admin['id']}|"
        all_tickets = [
            t for t in all_tickets
            if t.adminNotes and assignee_tag in (t.adminNotes or "")
        ]

    return {
        "total": len(all_tickets),
        "new": sum(1 for t in all_tickets if t.status == "new"),
        "processing": sum(1 for t in all_tickets if t.status == "processing"),
        "open": sum(1 for t in all_tickets if t.status == "open"),
        "in_progress": sum(1 for t in all_tickets if t.status == "in_progress"),
        "resolved": sum(1 for t in all_tickets if t.status == "resolved"),
        "closed": sum(1 for t in all_tickets if t.status == "closed"),
        "inbound_email": sum(1 for t in all_tickets if t.source == "email"),
        "web": sum(1 for t in all_tickets if t.source != "email"),
    }


@router.get("/admin/jobs/horizon")
async def admin_jobs_horizon(admin: dict = Depends(get_admin_user)):
    """
    Horizon-style real-time dashboard endpoint querying pgboss.job directly inside PostgreSQL.
    Returns live job counts by state, active jobs, recent completions, and failure diagnostics.
    """
    try:
        jobs = await db.query_raw('SELECT id, name, priority, state, data, output, created_on as "createdOn", started_on as "startedOn", completed_on as "completedOn" FROM pgboss.job ORDER BY created_on DESC LIMIT 100')
    except Exception as e:
        jobs = []

    if isinstance(jobs, list):
        state_counts = {
            "total": len(jobs),
            "created": sum(1 for j in jobs if j.get("state") == "created"),
            "active": sum(1 for j in jobs if j.get("state") == "active"),
            "completed": sum(1 for j in jobs if j.get("state") == "completed"),
            "failed": sum(1 for j in jobs if j.get("state") in ("failed", "cancelled", "expired")),
        }
    else:
        jobs = []
        state_counts = {"total": 0, "created": 0, "active": 0, "completed": 0, "failed": 0}

    return {
        "status": "online",
        "engine": "pg-boss (PostgreSQL Job Queue)",
        "stats": state_counts,
        "jobs": jobs
    }


@router.delete("/admin/jobs/clear-failed")
async def admin_clear_failed_jobs(admin: dict = Depends(get_admin_user)):
    """
    Clears old failed or cancelled diagnostic jobs from the pgboss.job table.
    """
    try:
        await db.execute_raw("DELETE FROM pgboss.job WHERE state::text IN ('failed', 'cancelled', 'expired')")
        try:
            await db.execute_raw("DELETE FROM pgboss.archive WHERE state::text IN ('failed', 'cancelled', 'expired')")
        except Exception:
            pass
        return {"success": True, "message": "Cleared failed jobs from pg-boss queue."}
    except Exception as e:
        print(f"❌ [admin_clear_failed_jobs] Error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/admin/analytics")
async def admin_support_analytics(admin: dict = Depends(get_admin_user)):
    """
    Support dashboard analytics via PostgreSQL stored function.
    """
    result = await db.query_raw("SELECT support_analytics($1) AS data", admin["id"])
    return result[0]["data"]


@router.get("/admin/analytics/daily")
async def admin_support_daily(admin: dict = Depends(get_admin_user)):
    """
    Daily ticket counts via PostgreSQL stored function.
    """
    result = await db.query_raw("SELECT support_analytics_daily($1) AS data", admin["id"])
    return result[0]["data"]


@router.get("/admin/{ticket_id}")
async def admin_get_ticket(
    ticket_id: str,
    admin: dict = Depends(get_admin_user),
):
    """
    Admin endpoint to get a single ticket by ID or Ticket Number.
    """
    clean_id = ticket_id.strip()
    clean_id_no_hash = clean_id.lstrip("#")
    ticket = await db.support_tickets.find_first(
        where={
            "OR": [
                {"id": clean_id},
                {"ticketNumber": clean_id},
                {"id": clean_id_no_hash},
                {"ticketNumber": clean_id_no_hash},
                {"ticketNumber": f"#{clean_id_no_hash}"},
            ]
        }
    )
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket not found ({clean_id})")

    user_obj = await db.user.find_unique(where={"id": admin["id"]})
    is_supreme = getattr(user_obj, "isSupreme", False) if user_obj else False
    if not is_supreme:
        assignee_tag = f"[ASSIGNED_TO:{admin['id']}|"
        if not ticket.adminNotes or assignee_tag not in (ticket.adminNotes or ""):
            raise HTTPException(status_code=403, detail="Access denied: ticket not assigned to you")

    user_map = {}
    if ticket.userId:
        user = await db.user.find_unique(where={"id": ticket.userId})
        if user:
            user_map[user.id] = user

    replies = await fetch_ticket_replies(ticket.id)
    return ticket_to_dict(ticket, user_map, replies)


@router.put("/admin/{ticket_id}/status")
async def admin_update_ticket_status(
    ticket_id: str,
    req: UpdateTicketStatusRequest,
    admin: dict = Depends(get_admin_user),
):
    """
    Admin endpoint to update ticket status, priority, and notes.
    """
    clean_id = ticket_id.strip()
    clean_id_no_hash = clean_id.lstrip("#")
    ticket = await db.support_tickets.find_first(
        where={
            "OR": [
                {"id": clean_id},
                {"ticketNumber": clean_id},
                {"id": clean_id_no_hash},
                {"ticketNumber": clean_id_no_hash},
                {"ticketNumber": f"#{clean_id_no_hash}"},
            ]
        }
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    data_to_update = {}
    if req.status is not None:
        data_to_update["status"] = req.status
    if req.category is not None:
        data_to_update["category"] = req.category
    if req.admin_notes is not None:
        data_to_update["adminNotes"] = req.admin_notes
    if req.priority is not None:
        data_to_update["priority"] = req.priority

    users = await db.user.find_many()
    user_map = {u.id: u for u in users}
    replies = await fetch_ticket_replies(ticket.id)

    if not data_to_update:
        return ticket_to_dict(ticket, user_map, replies)

    updated_ticket = await db.support_tickets.update(
        where={"id": ticket.id},
        data=data_to_update,
    )
    return ticket_to_dict(updated_ticket, user_map, replies)


@router.post("/admin/{ticket_id}/replies")
async def admin_create_ticket_reply(
    ticket_id: str,
    req: CreateTicketReplyRequest,
    admin: dict = Depends(get_admin_user),
):
    """
    Admin endpoint to submit a reply to a support ticket.
    """
    await ensure_ticket_replies_table()
    clean_id = ticket_id.strip()
    clean_id_no_hash = clean_id.lstrip("#")
    ticket = await db.support_tickets.find_first(
        where={
            "OR": [
                {"id": clean_id},
                {"ticketNumber": clean_id},
                {"id": clean_id_no_hash},
                {"ticketNumber": clean_id_no_hash},
                {"ticketNumber": f"#{clean_id_no_hash}"},
            ]
        }
    )
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket not found ({clean_id})")

    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Reply message cannot be empty")

    sender_name = req.sender_name or admin.get("name") or "Support Team"
    reply_id = str(uuid.uuid4())

    await db.query_raw(
        'INSERT INTO ticket_replies (id, ticket_id, sender_name, sender_role, sender_type, message, created_at) VALUES ($1, $2, $3, $4, $5, $6, NOW())',
        reply_id,
        ticket.id,
        sender_name,
        "admin",
        "agent",
        req.message.strip(),
    )

    if ticket.status == "open":
        await db.support_tickets.update(
            where={"id": ticket.id}, data={"status": "in_progress"}
        )

    if ticket.senderEmail:
        # Validate recipient email exists in the application before sending
        recipient_user = await db.user.find_unique(where={"email": ticket.senderEmail.lower()})
        if not recipient_user:
            print(f"⚠️ [admin-reply] Recipient email {ticket.senderEmail} not registered, skipping outbound email")
        else:
            html_email = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #0d9488; color: white; padding: 16px 24px; border-radius: 8px 8px 0 0;">
                    <h2 style="margin: 0; font-size: 16px;">RoadLancer Support</h2>
                    <p style="margin: 4px 0 0; font-size: 13px; opacity: 0.9;">Ticket #{ticket.ticketNumber}</p>
                </div>
                <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none;">
                    <p style="color: #374151; font-size: 14px;">Hi {ticket.senderName or ''},</p>
                    <p style="color: #374151; font-size: 14px;">{sender_name} has replied to your support ticket:</p>
                    <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e5e7eb; margin: 16px 0;">
                        <p style="color: #1f2937; font-size: 14px; white-space: pre-wrap;">{req.message.strip()}</p>
                    </div>
                    <p style="color: #6b7280; font-size: 12px; margin-top: 24px;">
                        You can reply directly to this email to continue the conversation.
                    </p>
                </div>
            </div>
            """
            # Use in_reply_to and references for proper email threading
            # If we have in_reply_to from incoming email, use it; otherwise use gmail_message_id
            reply_to_message_id = getattr(ticket, 'inReplyTo', None) or getattr(ticket, 'gmailMessageId', None)
            # If we have references from incoming email, append our message-id; otherwise start with reply_to_message_id
            reply_references = getattr(ticket, 'references', None)
            if reply_references and reply_to_message_id:
                # Append our reply's message-id will be added by Gmail API
                references_header = f"{reply_references} {reply_to_message_id}"
            elif reply_to_message_id:
                references_header = reply_to_message_id
            else:
                references_header = None
            
            asyncio.create_task(
                asyncio.to_thread(
                    send_reply_email,
                    ticket.senderEmail,
                    ticket.subject,
                    html_email,
                    ticket.ticketNumber,
                    sender_name,
                    gmail_thread_id=getattr(ticket, 'gmailThreadId', None),
                    gmail_message_id=reply_to_message_id,
                    references=references_header,
                )
            )

    users = await db.user.find_many()
    user_map = {u.id: u for u in users}
    replies = await fetch_ticket_replies(ticket.id)
    updated_ticket = await db.support_tickets.find_unique(where={"id": ticket.id})
    return ticket_to_dict(updated_ticket or ticket, user_map, replies)


@router.get("/tickets/{ticket_id}")
async def user_get_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
):
    clean_id = ticket_id.strip()
    clean_id_no_hash = clean_id.lstrip("#")
    ticket = await db.support_tickets.find_first(
        where={
            "OR": [
                {"id": clean_id},
                {"ticketNumber": clean_id},
                {"id": clean_id_no_hash},
                {"ticketNumber": clean_id_no_hash},
                {"ticketNumber": f"#{clean_id_no_hash}"},
            ]
        }
    )
    if not ticket or ticket.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Ticket not found")

    users = await db.user.find_many()
    user_map = {u.id: u for u in users}
    replies = await fetch_ticket_replies(ticket.id)
    return ticket_to_dict(ticket, user_map, replies)


@router.post("/tickets/{ticket_id}/replies")
async def user_create_ticket_reply(
    ticket_id: str,
    req: CreateTicketReplyRequest,
    current_user: dict = Depends(get_current_user),
):
    await ensure_ticket_replies_table()
    clean_id = ticket_id.strip()
    clean_id_no_hash = clean_id.lstrip("#")
    ticket = await db.support_tickets.find_first(
        where={
            "OR": [
                {"id": clean_id},
                {"ticketNumber": clean_id},
                {"id": clean_id_no_hash},
                {"ticketNumber": clean_id_no_hash},
                {"ticketNumber": f"#{clean_id_no_hash}"},
            ]
        }
    )
    if not ticket or ticket.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Reply message cannot be empty")

    sender_name = current_user.get("name") or ticket.senderName or "User"
    reply_id = str(uuid.uuid4())

    await db.query_raw(
        'INSERT INTO ticket_replies (id, ticket_id, sender_name, sender_role, sender_type, message, created_at) VALUES ($1, $2, $3, $4, $5, $6, NOW())',
        reply_id,
        ticket.id,
        sender_name,
        "user",
        "customer",
        req.message.strip(),
    )

    users = await db.user.find_many()
    user_map = {u.id: u for u in users}
    replies = await fetch_ticket_replies(ticket.id)
    return ticket_to_dict(ticket, user_map, replies)


@router.get("/test-email")
async def test_email_endpoint():
    """Test endpoint to verify email sending works on Railway."""
    result = await asyncio.to_thread(
        send_reply_email,
        "support.roadlancer@gmail.com",
        "Test Email from RoadLancer",
        "<h1>Test</h1><p>If you see this, email sending works on Railway!</p>",
        "TICK-TEST",
        "RoadLancer Test",
    )
    return {"email_sent": result}


@router.post("/webhook/gmail")
async def handle_gmail_pubsub(request: Request):
    """
    Webhook endpoint for Gmail Pub/Sub push notifications.
    When a new email arrives in support.roadlancer@gmail.com, Google sends
    a notification here. We fetch the email via Gmail API and create a ticket.
    """
    try:
        raw_body = await request.body()
        payload = json.loads(raw_body)

        message_data = payload.get("message", {})
        data_encoded = message_data.get("data", "")

        if not data_encoded:
            return {"received": True, "ignored": True, "reason": "no data"}

        import base64 as b64
        data_json = json.loads(b64.b64decode(data_encoded).decode("utf-8"))
        email_address = data_json.get("emailAddress", "")
        history_id = data_json.get("historyId", "")

        logger.info(f"Gmail notification: email={email_address}, historyId={history_id}")

        # Ensure threading columns exist (migration)
        await ensure_ticket_replies_table()

        from app.gmail_client import list_recent_emails, mark_email_as_read

        emails = list_recent_emails(max_results=5)

        created_tickets = []
        for email in emails:
            from_email = email.get("from", "")
            subject = email.get("subject", "No Subject")
            body = email.get("body", "") or email.get("snippet", "")

            if not from_email or not subject:
                continue

            # Validate sender email exists in the application
            user = await db.user.find_unique(where={"email": from_email.lower()})
            if not user:
                logger.info(f"Gmail webhook: Email {from_email} not registered, skipping")
                continue

            user_id = user.id
            sender_name = user.name or from_email.split("@")[0].replace(".", " ").title()

            ticket_number = await generate_unique_ticket_number()

            try:
                ticket = await db.support_tickets.create(
                    data={
                        "ticketNumber": ticket_number,
                        "senderEmail": from_email.lower(),
                        "senderName": sender_name,
                        "subject": subject[:200],
                        "message": body[:5000],
                        "category": "general",
                        "priority": "normal",
                        "source": "email",
                        "userId": user_id,
                        "status": "new",
                    }
                )
                asyncio.create_task(classify_ticket_background(ticket.id, subject[:200], body[:5000], sender_name))
                created_tickets.append(ticket_number)
                logger.info(f"Created ticket {ticket_number} from Gmail email by {from_email}")
            except Exception as e:
                logger.error(f"Failed to create ticket from email: {e}")

        return {
            "received": True,
            "tickets_created": created_tickets,
            "count": len(created_tickets),
        }

    except Exception as e:
        logger.error(f"Gmail webhook error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Gmail webhook error: {str(e)}")


@router.get("/gmail/status")
async def gmail_status():
    """Check Gmail API connection status."""
    from app.gmail_client import _get_gmail_service

    service = _get_gmail_service()
    gmail_user = os.getenv("GMAIL_USER_EMAIL", "")
    service_account = os.getenv("GMAIL_SERVICE_ACCOUNT_JSON", "")

    return {
        "configured": bool(service),
        "gmail_user": gmail_user,
        "service_account_set": bool(service_account),
        "service_alive": service is not None,
    }


@router.post("/notify-email")
async def send_notification_email(
    request: Request,
    x_webhook_secret: Optional[str] = Header(None, alias="x-webhook-secret"),
):
    """
    Internal endpoint to send notification email after AI auto-resolution.
    Called by auth-server after ticket is auto-resolved.
    """
    expected_secret = os.getenv("SUPPORT_WEBHOOK_SECRET", "roadlancer-webhook-secret-2026")
    provided_secret = x_webhook_secret
    
    if provided_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    
    try:
        data = await request.json()
        ticket_id = data.get("ticketId")
        recipient_email = data.get("recipientEmail")
        recipient_name = data.get("recipientName", "")
        subject = data.get("subject", "")
        reply_message = data.get("replyMessage", "")
        ticket_number = data.get("ticketNumber", "")
        
        if not ticket_id or not recipient_email or not reply_message:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Validate recipient email exists
        user = await db.user.find_unique(where={"email": recipient_email.lower()})
        if not user:
            print(f"⚠️ [notify-email] Recipient {recipient_email} not registered, skipping")
            return {"sent": False, "reason": "email not registered"}
        
        # Fetch ticket for threading info
        ticket = await db.support_tickets.find_unique(where={"id": ticket_id})
        if not ticket:
            ticket = await db.support_tickets.find_unique(where={"ticketNumber": ticket_id})
        
        html_email = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #0d9488; color: white; padding: 16px 24px; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0; font-size: 16px;">RoadLancer Support</h2>
                <p style="margin: 4px 0 0; font-size: 13px; opacity: 0.9;">Ticket #{ticket_number}</p>
            </div>
            <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none;">
                <p style="color: #374151; font-size: 14px;">Hi {recipient_name or ''},</p>
                <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e5e7eb; margin: 16px 0;">
                    <p style="color: #1f2937; font-size: 14px; white-space: pre-wrap;">{reply_message}</p>
                </div>
                <p style="color: #6b7280; font-size: 12px; margin-top: 24px;">
                    This is an automated response from RoadLancer AI Support.
                </p>
            </div>
        </div>
        """
        
        # Use threading info if available
        reply_to_message_id = None
        references_header = None
        if ticket:
            reply_to_message_id = getattr(ticket, 'inReplyTo', None) or getattr(ticket, 'gmailMessageId', None)
            references_header = getattr(ticket, 'references', None)
        
        # Send email synchronously and report result
        email_result = await asyncio.to_thread(
            send_reply_email,
            recipient_email,
            subject,
            html_email,
            ticket_number,
            "RoadLancer AI Agent",
            gmail_thread_id=getattr(ticket, 'gmailThreadId', None) if ticket else None,
            gmail_message_id=reply_to_message_id,
            references=references_header,
        )
        
        if email_result:
            print(f"✅ [notify-email] AI resolution email sent to {recipient_email} (ticket {ticket_number})")
            return {"sent": True, "recipient": recipient_email}
        else:
            print(f"❌ [notify-email] Failed to send email to {recipient_email} (ticket {ticket_number})")
            return {"sent": False, "reason": "email sending failed", "recipient": recipient_email}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [notify-email] Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


