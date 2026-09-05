import asyncio
from app.core.database import AsyncSessionFactory
from app.infrastructure.db.repositories.sqlalchemy_order_repository import SQLAlchemyOrderRepository

async def main():
    async with AsyncSessionFactory() as session:
        repo = SQLAlchemyOrderRepository(session)
        reqs = await repo.list_open_clothing_requests()
        for r in reqs:
            print(f"Request {r.request_id} client: {r.client}")

asyncio.run(main())
