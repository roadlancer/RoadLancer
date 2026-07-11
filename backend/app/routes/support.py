import os
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from app.database import db
from app.routes.auth import get_current_user
from app.routes.admin import get_admin_user

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
            import traceback
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

    last_exc = None
    for _attempt in range(3):
        try:
            # Check if sender matches an existing user
            user = await db.user.find_unique(where={"email": req.from_email.lower()})
            user_id = user.id if user else None
            sender_name = req.from_name or (user.name if user else req.from_email)

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
                    "status": "open",
                }
            )
            break
        except Exception as e:
            import traceback
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
                import asyncio
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
            "status": "open",
        }
    )

    # Fetch full user object for dict conversion
    db_user = await db.user.find_unique(where={"id": user["id"]})
    user_map = {user["id"]: db_user} if db_user else {}
    return ticket_to_dict(ticket, user_map)



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

    if status and status in ("open", "in_progress", "resolved", "closed"):
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
    admin: dict = Depends(get_admin_user),
):
    """
    Admin endpoint to list all support tickets across all users and sources.
    Supreme admins see all tickets. Regular agents see only tickets assigned to them.
    """
    tickets = await db.support_tickets.find_many()

    user = await db.user.find_unique(where={"id": admin["id"]})
    is_supreme = getattr(user, "isSupreme", False) if user else False

    if not is_supreme:
        assignee_tag = f"[ASSIGNED_TO:{admin['id']}|"
        tickets = [
            t for t in tickets
            if t.adminNotes and assignee_tag in (t.adminNotes or "")
        ]

    if status and status in ("open", "in_progress", "resolved", "closed"):
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
async def admin_ticket_counts(admin: dict = Depends(get_admin_user)):
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
        "open": sum(1 for t in all_tickets if t.status == "open"),
        "in_progress": sum(1 for t in all_tickets if t.status == "in_progress"),
        "resolved": sum(1 for t in all_tickets if t.status == "resolved"),
        "closed": sum(1 for t in all_tickets if t.status == "closed"),
        "inbound_email": sum(1 for t in all_tickets if t.source == "email"),
        "web": sum(1 for t in all_tickets if t.source != "email"),
    }


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

