import asyncio
from app.core.database import AsyncSessionFactory
from app.infrastructure.db.repositories.sqlalchemy_rbac_repository import SQLAlchemyRBACRepository
from sqlalchemy import select
from app.infrastructure.db.models.rbac_model import RoleModel

async def main():
    async with AsyncSessionFactory() as session:
        repo = SQLAlchemyRBACRepository(session)
        print('client role:', await repo.get_role_by_name('client'))
        print('tailor role:', await repo.get_role_by_name('tailor'))

        # Also just print all roles to be sure
        stmt = select(RoleModel)
        result = await session.execute(stmt)
        roles = result.scalars().all()
        print('all roles:', [r.name for r in roles])

if __name__ == "__main__":
    asyncio.run(main())
