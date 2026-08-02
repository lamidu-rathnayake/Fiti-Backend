from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.user import User, Client, Seller, MeasurementProfile
from app.domain.repositories.user_repository import (
    AbstractUserRepository,
    AbstractClientRepository,
    AbstractSellerRepository,
    AbstractMeasurementProfileRepository,
)
from app.infrastructure.db.models.user_model import (
    UserModel,
    ClientModel,
    SellerModel,
    MeasurementProfileModel,
)


class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        model = UserModel.from_domain(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def update(self, user: User) -> User:
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.name = user.name
            model.whatsapp_number = user.whatsapp_number
            model.address = user.address
            model.city = user.city
            model.postal_code = user.postal_code
            model.gender = user.gender
            model.age = user.age
            model.profile_image = user.profile_image
            model.is_active = user.is_active
            await self.session.commit()
            await self.session.refresh(model)
            return model.to_domain()
        return await self.create(user)

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def delete(self, user_id: str) -> bool:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False


class SQLAlchemyClientRepository(AbstractClientRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, client: Client) -> Client:
        model = ClientModel(id=client.id)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def get_by_id(self, client_id: str) -> Optional[Client]:
        stmt = select(ClientModel).where(ClientModel.id == client_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None


class SQLAlchemySellerRepository(AbstractSellerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, seller: Seller) -> Seller:
        model = SellerModel(
            id=seller.id,
            nic_front=seller.nic_front,
            nic_rear=seller.nic_rear,
            is_verified=seller.is_verified,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def get_by_id(self, seller_id: str) -> Optional[Seller]:
        stmt = select(SellerModel).where(SellerModel.id == seller_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def update(self, seller: Seller) -> Seller:
        stmt = select(SellerModel).where(SellerModel.id == seller.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.nic_front = seller.nic_front
            model.nic_rear = seller.nic_rear
            model.is_verified = seller.is_verified
            await self.session.commit()
            await self.session.refresh(model)
            return model.to_domain()
        return await self.create(seller)


class SQLAlchemyMeasurementProfileRepository(AbstractMeasurementProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, profile: MeasurementProfile) -> MeasurementProfile:
        stmt = select(MeasurementProfileModel).where(MeasurementProfileModel.user_id == profile.user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.chest = profile.chest
            model.waist = profile.waist
            model.shoulder = profile.shoulder
            model.sleeve = profile.sleeve
            model.neck = profile.neck
            model.hip = profile.hip
            model.inseam = profile.inseam
            model.length = profile.length
            model.notes = profile.notes
        else:
            model = MeasurementProfileModel(
                user_id=profile.user_id,
                chest=profile.chest,
                waist=profile.waist,
                shoulder=profile.shoulder,
                sleeve=profile.sleeve,
                neck=profile.neck,
                hip=profile.hip,
                inseam=profile.inseam,
                length=profile.length,
                notes=profile.notes,
            )
            self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def get_by_user_id(self, user_id: str) -> Optional[MeasurementProfile]:
        stmt = select(MeasurementProfileModel).where(MeasurementProfileModel.user_id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None
