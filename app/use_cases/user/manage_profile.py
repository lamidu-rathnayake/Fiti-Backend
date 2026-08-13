
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
from app.use_cases.dtos.user_dto import (
    ClientOutputDTO,
    ClientRegisterDTO,
    MeasurementProfileDTO,
    MeasurementProfileOutputDTO,
    TailorOutputDTO,
    TailorRegisterDTO,
)


class ManageProfileUseCase:
    """
    Handles profile registration and measurement management.
    User identity (name, email, auth) is owned by Firebase — this use case
    only manages the PostgreSQL profile extension records.
    """

    def __init__(
        self,
        client_repository: AbstractClientRepository,
        tailor_repository: AbstractTailorRepository,
        measurement_repository: AbstractMeasurementProfileRepository,
    ):
        self.client_repository = client_repository
        self.tailor_repository = tailor_repository
        self.measurement_repository = measurement_repository

    async def register_client(self, dto: ClientRegisterDTO) -> ClientOutputDTO:
        existing = await self.client_repository.get_by_id(dto.id)
        if existing:
            raise ProfileAlreadyExistsError(dto.id, role="client")
        client = Client(id=dto.id)
        saved = await self.client_repository.create(client)
        return ClientOutputDTO(id=saved.id, created_at=saved.created_at, updated_at=saved.updated_at)

    async def register_tailor(self, dto: TailorRegisterDTO) -> TailorOutputDTO:
        existing = await self.tailor_repository.get_by_id(dto.id)
        if existing:
            raise ProfileAlreadyExistsError(dto.id, role="tailor")
        tailor = Tailor(id=dto.id, nic_front=dto.nic_front, nic_rear=dto.nic_rear)
        saved = await self.tailor_repository.create(tailor)
        return TailorOutputDTO(
            id=saved.id,
            nic_front=saved.nic_front,
            nic_rear=saved.nic_rear,
            is_verified=saved.is_verified,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def get_client_profile(self, client_id: str) -> ClientOutputDTO:
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        return ClientOutputDTO(id=client.id, created_at=client.created_at, updated_at=client.updated_at)

    async def get_tailor_profile(self, tailor_id: str) -> TailorOutputDTO:
        tailor = await self.tailor_repository.get_by_id(tailor_id)
        if not tailor:
            raise TailorNotFoundError(tailor_id)
        return TailorOutputDTO(
            id=tailor.id,
            nic_front=tailor.nic_front,
            nic_rear=tailor.nic_rear,
            is_verified=tailor.is_verified,
            created_at=tailor.created_at,
            updated_at=tailor.updated_at,
        )

    async def upsert_measurement_profile(self, dto: MeasurementProfileDTO) -> MeasurementProfileOutputDTO:
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

    async def get_measurement_profile(self, client_id: str) -> MeasurementProfileOutputDTO | None:
        profile = await self.measurement_repository.get_by_client_id(client_id)
        return self._to_measurement_output_dto(profile) if profile else None

    def _to_measurement_output_dto(self, p: MeasurementProfile) -> MeasurementProfileOutputDTO:
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

