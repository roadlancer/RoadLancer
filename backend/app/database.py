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


async def disconnect_db():
    await db.disconnect()
