import asyncio
from app.core.database import engine
from app.infrastructure.db.base import Base

async def test():
    print("Testing DB connection...")
    try:
        async with engine.begin() as conn:
            print("Connected to DB successfully.")
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created.")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
