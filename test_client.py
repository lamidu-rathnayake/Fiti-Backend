import asyncio
from app.infrastructure.db.base import async_session
from app.infrastructure.db.repositories.sqlalchemy_order_repository import SQLAlchemyOrderRepository

async def main():
    async with async_session() as session:
        repo = SQLAlchemyOrderRepository(session)
        reqs = await repo.list_open_clothing_requests()
        for r in reqs:
            print(f"Request {r.request_id} client: {r.client}")

asyncio.run(main())
