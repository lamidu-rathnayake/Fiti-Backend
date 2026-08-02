from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.user import Client, Seller, MeasurementProfile
from app.domain.repositories.profile_repository import (
    AbstractClientRepository,
    AbstractSellerRepository,
    AbstractMeasurementProfileRepository,
)
from app.infrastructure.db.models.user_model import (
    ClientModel,
    SellerModel,
    MeasurementProfileModel,
)


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

    async def update_verification(self, seller_id: str, is_verified: bool) -> Seller:
        stmt = select(SellerModel).where(SellerModel.id == seller_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        model.is_verified = is_verified
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()


class SQLAlchemyMeasurementProfileRepository(AbstractMeasurementProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile: MeasurementProfile) -> MeasurementProfile:
        model = MeasurementProfileModel(
            client_id=profile.client_id,
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

    async def get_by_client_id(self, client_id: str) -> Optional[MeasurementProfile]:
        stmt = select(MeasurementProfileModel).where(MeasurementProfileModel.client_id == client_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def update(self, profile: MeasurementProfile) -> MeasurementProfile:
        stmt = select(MeasurementProfileModel).where(
            MeasurementProfileModel.client_id == profile.client_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        for field in ["chest", "waist", "shoulder", "sleeve", "neck", "hip", "inseam", "length", "notes"]:
            value = getattr(profile, field)
            if value is not None:
                setattr(model, field, value)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()
