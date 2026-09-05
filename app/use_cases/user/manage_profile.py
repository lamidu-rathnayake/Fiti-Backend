import logging

from app.domain.entities.user import Client, MeasurementProfile, Tailor
from app.domain.exceptions.user import (
    ClientNotFoundError,
    ProfileAlreadyExistsError,
    TailorNotFoundError,
)
from app.domain.repositories.profile_repository import (
    AbstractClientRepository,
    AbstractMeasurementProfileRepository,
    AbstractTailorRepository,
)
from app.domain.repositories.rbac_repository import AbstractRBACRepository
from app.use_cases.dtos.user_dto import (
    ClientOutputDTO,
    ClientRegisterDTO,
    ClientUpdateDTO,
    MeasurementProfileDTO,
    MeasurementProfileOutputDTO,
    TailorOutputDTO,
    TailorRegisterDTO,
    TailorUpdateDTO,
)


logger = logging.getLogger(__name__)


class ManageProfileUseCase:
    """
    Handles profile registration, update, and measurement management.
    User identity (name, email, auth) is owned by Firebase — this use case
    only manages the PostgreSQL profile extension records.
    """

    def __init__(
        self,
        client_repository: AbstractClientRepository,
        tailor_repository: AbstractTailorRepository,
        measurement_repository: AbstractMeasurementProfileRepository,
        rbac_repository: AbstractRBACRepository = None,
    ):
        self.client_repository = client_repository
        self.tailor_repository = tailor_repository
        self.measurement_repository = measurement_repository
        self.rbac_repository = rbac_repository

    async def register_client(self, dto: ClientRegisterDTO) -> ClientOutputDTO:
        existing = await self.client_repository.get_by_id(dto.id)
        if existing:
            raise ProfileAlreadyExistsError(dto.id, role="client")
        client = Client(
            id=dto.id,
            display_name=dto.display_name,
            email=dto.email,
            photo_url=dto.photo_url,
            phone=dto.phone,
            city=dto.city,
            address=dto.address,
            latitude=dto.latitude,
            longitude=dto.longitude,
        )
        saved = await self.client_repository.create(client)
        if self.rbac_repository:
            role = await self.rbac_repository.get_role_by_name("client")
            if role and role.id is not None:
                await self.rbac_repository.assign_role_to_user(saved.id, role.id)
                logger.info("Assigned 'client' role to user %s", saved.id)
            else:
                logger.error(
                    "ROLE ASSIGNMENT FAILED: 'client' role not found in roles table for user %s. "
                    "Ensure the roles table is seeded with name='client'.",
                    saved.id,
                )
                raise RuntimeError(
                    "Role 'client' not found in the roles table. "
                    "Run schema.sql seed data or insert it manually before registering users."
                )
        return self._to_client_output_dto(saved)

    async def register_tailor(self, dto: TailorRegisterDTO) -> TailorOutputDTO:
        existing = await self.tailor_repository.get_by_id(dto.id)
        if existing:
            raise ProfileAlreadyExistsError(dto.id, role="tailor")
        tailor = Tailor(
            id=dto.id,
            display_name=dto.display_name,
            email=dto.email,
            photo_url=dto.photo_url,
            nic_front=dto.nic_front,
            nic_rear=dto.nic_rear,
            phone=dto.phone,
            city=dto.city,
            address=dto.address,
            latitude=dto.latitude,
            longitude=dto.longitude,
        )
        saved = await self.tailor_repository.create(tailor)
        if self.rbac_repository:
            role = await self.rbac_repository.get_role_by_name("tailor")
            if role and role.id is not None:
                await self.rbac_repository.assign_role_to_user(saved.id, role.id)
                logger.info("Assigned 'tailor' role to user %s", saved.id)
            else:
                logger.error(
                    "ROLE ASSIGNMENT FAILED: 'tailor' role not found in roles table for user %s. "
                    "Ensure the roles table is seeded with name='tailor'.",
                    saved.id,
                )
                raise RuntimeError(
                    "Role 'tailor' not found in the roles table. "
                    "Run schema.sql seed data or insert it manually before registering users."
                )
        return self._to_tailor_output_dto(saved)

    async def get_client_profile(self, client_id: str) -> ClientOutputDTO:
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        return self._to_client_output_dto(client)

    async def get_tailor_profile(self, tailor_id: str) -> TailorOutputDTO:
        tailor = await self.tailor_repository.get_by_id(tailor_id)
        if not tailor:
            raise TailorNotFoundError(tailor_id)
        return self._to_tailor_output_dto(tailor)

    async def update_client_profile(self, dto: ClientUpdateDTO) -> ClientOutputDTO:
        """Partially update a client's contact profile (phone, city, address)."""
        existing = await self.client_repository.get_by_id(dto.id)
        if not existing:
            raise ClientNotFoundError(dto.id)
        # Only overwrite fields that were explicitly provided (not None)
        updated_client = Client(
            id=existing.id,
            display_name=dto.display_name if dto.display_name is not None else existing.display_name,
            email=dto.email if dto.email is not None else existing.email,
            photo_url=dto.photo_url if dto.photo_url is not None else existing.photo_url,
            phone=dto.phone if dto.phone is not None else existing.phone,
            city=dto.city if dto.city is not None else existing.city,
            address=dto.address if dto.address is not None else existing.address,
            latitude=dto.latitude if dto.latitude is not None else existing.latitude,
            longitude=dto.longitude if dto.longitude is not None else existing.longitude,
        )
        saved = await self.client_repository.update(updated_client)
        return self._to_client_output_dto(saved)

    async def update_tailor_profile(self, dto: TailorUpdateDTO) -> TailorOutputDTO:
        """Partially update a tailor's contact profile (phone, city, address, nic images)."""
        existing = await self.tailor_repository.get_by_id(dto.id)
        if not existing:
            raise TailorNotFoundError(dto.id)
        updated_tailor = Tailor(
            id=existing.id,
            display_name=dto.display_name if dto.display_name is not None else existing.display_name,
            email=dto.email if dto.email is not None else existing.email,
            photo_url=dto.photo_url if dto.photo_url is not None else existing.photo_url,
            nic_front=dto.nic_front if dto.nic_front is not None else existing.nic_front,
            nic_rear=dto.nic_rear if dto.nic_rear is not None else existing.nic_rear,
            is_verified=existing.is_verified,
            phone=dto.phone if dto.phone is not None else existing.phone,
            city=dto.city if dto.city is not None else existing.city,
            address=dto.address if dto.address is not None else existing.address,
            latitude=dto.latitude if dto.latitude is not None else existing.latitude,
            longitude=dto.longitude if dto.longitude is not None else existing.longitude,
        )
        saved = await self.tailor_repository.update(updated_tailor)
        return self._to_tailor_output_dto(saved)

    async def upsert_measurement_profile(
        self, dto: MeasurementProfileDTO
    ) -> MeasurementProfileOutputDTO:
        existing = await self.measurement_repository.get_by_client_id(dto.client_id)
        profile = MeasurementProfile(
            client_id=dto.client_id,
            chest=dto.chest,
            waist=dto.waist,
            shoulder=dto.shoulder,
            sleeve=dto.sleeve,
            neck=dto.neck,
            hip=dto.hip,
            inseam=dto.inseam,
            length=dto.length,
            notes=dto.notes,
        )
        saved = await (
            self.measurement_repository.update(profile)
            if existing
            else self.measurement_repository.create(profile)
        )
        return self._to_measurement_output_dto(saved)

    async def get_measurement_profile(
        self, client_id: str
    ) -> MeasurementProfileOutputDTO | None:
        profile = await self.measurement_repository.get_by_client_id(client_id)
        return self._to_measurement_output_dto(profile) if profile else None

    # ── Private helpers ─────────────────────────────────────────────────

    def _to_client_output_dto(self, client: Client) -> ClientOutputDTO:
        return ClientOutputDTO(
            id=client.id,
            display_name=client.display_name,
            email=client.email,
            photo_url=client.photo_url,
            phone=client.phone,
            city=client.city,
            address=client.address,
            latitude=client.latitude,
            longitude=client.longitude,
            created_at=client.created_at,
            updated_at=client.updated_at,
        )

    def _to_tailor_output_dto(self, tailor: Tailor) -> TailorOutputDTO:
        return TailorOutputDTO(
            id=tailor.id,
            display_name=tailor.display_name,
            email=tailor.email,
            photo_url=tailor.photo_url,
            nic_front=tailor.nic_front,
            nic_rear=tailor.nic_rear,
            is_verified=tailor.is_verified,
            phone=tailor.phone,
            city=tailor.city,
            address=tailor.address,
            latitude=tailor.latitude,
            longitude=tailor.longitude,
            created_at=tailor.created_at,
            updated_at=tailor.updated_at,
        )

    def _to_measurement_output_dto(
        self, p: MeasurementProfile
    ) -> MeasurementProfileOutputDTO:
        return MeasurementProfileOutputDTO(
            client_id=p.client_id,
            measurement_id=p.measurement_id,
            chest=p.chest,
            waist=p.waist,
            shoulder=p.shoulder,
            sleeve=p.sleeve,
            neck=p.neck,
            hip=p.hip,
            inseam=p.inseam,
            length=p.length,
            notes=p.notes,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
