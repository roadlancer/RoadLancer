import os
from prisma import Prisma

db = Prisma(
    datasource={
        'url': os.environ.get(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5433/roadlancer',
        )
    }
)


async def connect_db():
    await db.connect()
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
        await db.query_raw("UPDATE ticket_replies SET sender_type = 'customer' WHERE sender_role = 'user' AND sender_type = 'agent';")
    except Exception as e:
        pass


async def disconnect_db():
    await db.disconnect()
