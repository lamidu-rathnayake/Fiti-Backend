from typing import Optional
from app.domain.entities.user import MeasurementProfile
from app.domain.repositories.user_repository import AbstractMeasurementProfileRepository
from app.use_cases.dtos.user_dto import MeasurementProfileDTO


class ManageMeasurementProfileUseCase:
    def __init__(self, profile_repository: AbstractMeasurementProfileRepository):
        self.profile_repository = profile_repository

    async def upsert_profile(self, dto: MeasurementProfileDTO) -> MeasurementProfileDTO:
        entity = MeasurementProfile(
            user_id=dto.user_id,
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
        saved = await self.profile_repository.upsert(entity)
        return MeasurementProfileDTO(
            user_id=saved.user_id,
            chest=saved.chest,
            waist=saved.waist,
            shoulder=saved.shoulder,
            sleeve=saved.sleeve,
            neck=saved.neck,
            hip=saved.hip,
            inseam=saved.inseam,
            length=saved.length,
            notes=saved.notes,
        )

    async def get_profile(self, user_id: str) -> Optional[MeasurementProfileDTO]:
        saved = await self.profile_repository.get_by_user_id(user_id)
        if not saved:
            return None
        return MeasurementProfileDTO(
            user_id=saved.user_id,
            chest=saved.chest,
            waist=saved.waist,
            shoulder=saved.shoulder,
            sleeve=saved.sleeve,
            neck=saved.neck,
            hip=saved.hip,
            inseam=saved.inseam,
            length=saved.length,
            notes=saved.notes,
        )
