from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_manage_shop_use_case
from app.api.schemas.shop_schema import (
    GigCreateRequest,
    GigResponse,
    ShopCreateRequest,
    ShopWorkCreateRequest,
    ShopWorkSchema,
    ShopResponse,
    ShopUpdateRequest,
)
from app.core.security import require_verified_tailor
from app.domain.exceptions.shop import ShopNotFoundError
from app.use_cases.dtos.shop_dto import ShopCreateDTO, ShopUpdateDTO
from app.use_cases.shop.manage_shop import ManageShopUseCase

router = APIRouter(prefix="/shops", tags=["Shops"])


# ── List & Search (static paths must come before /{shop_id}) ───────────


@router.get("/", response_model=list[ShopResponse])
async def list_shops(
    skip: int = 0,
    limit: int = 100,
    city: str | None = None,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """List all shops, with optional city filter."""
    return await use_case.list_shops(skip=skip, limit=limit, city=city)


@router.get("/nearby", response_model=list[ShopResponse])
async def search_near_shops(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(10.0, description="Search radius in kilometers"),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Find tailor shops within a GPS radius. Must be registered before /{shop_id}."""
    return await use_case.search_near_location(lat=lat, lng=lng, radius_km=radius_km)


@router.get("/tailor/{tailor_id}", response_model=list[ShopResponse])
async def get_shops_by_tailor(
    tailor_id: str,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Get all shops owned by a specific tailor. Must be registered before /{shop_id}."""
    return await use_case.get_shops_by_tailor(tailor_id)


# ── Single Shop by ID ───────────────────────────────────────────────────


@router.get("/{shop_id}", response_model=ShopResponse)
async def get_shop(
    shop_id: int,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Get a shop by its ID."""
    try:
        return await use_case.get_shop_by_id(shop_id)
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ── Write Operations (tailor role required) ────────────────────────────


@router.post("/", response_model=ShopResponse, status_code=status.HTTP_201_CREATED)
async def create_shop(
    request: ShopCreateRequest,
    authenticated_uid: str = Depends(require_verified_tailor),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Register a shop owned by the authenticated tailor."""
    dto = ShopCreateDTO(
        tailor_id=authenticated_uid,
        shop_name=request.shop_name,
        specialty=request.specialty,
        shop_bio=request.shop_bio,
        shop_address=request.shop_address,
        city=request.city,
        contact_number=request.contact_number,
        registration_number=request.registration_number,
        latitude=request.latitude,
        longitude=request.longitude,
        profile_image_url=request.profile_image_url,
    )
    return await use_case.create_shop(dto)


@router.put("/{shop_id}", response_model=ShopResponse)
async def update_shop(
    shop_id: int,
    request: ShopUpdateRequest,
    authenticated_uid: str = Depends(require_verified_tailor),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Update a shop owned by the authenticated tailor."""
    try:
        shop = await use_case.get_shop_by_id(shop_id)
        if shop.tailor_id != authenticated_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this shop.",
            )
        dto = ShopUpdateDTO(
            shop_id=shop_id,
            shop_name=request.shop_name,
            specialty=request.specialty,
            shop_bio=request.shop_bio,
            shop_address=request.shop_address,
            city=request.city,
            contact_number=request.contact_number,
            registration_number=request.registration_number,
            latitude=request.latitude if request.latitude is not None else shop.latitude,
            longitude=request.longitude if request.longitude is not None else shop.longitude,
            profile_image_url=request.profile_image_url,
        )
        return await use_case.update_shop(dto)
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shop(
    shop_id: int,
    authenticated_uid: str = Depends(require_verified_tailor),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Delete a shop owned by the authenticated tailor."""
    try:
        shop = await use_case.get_shop_by_id(shop_id)
        if shop.tailor_id != authenticated_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this shop.",
            )
        await use_case.delete_shop(shop_id)
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/{shop_id}/works",
    response_model=ShopWorkSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_shop_work(
    shop_id: int,
    request: ShopWorkCreateRequest,
    authenticated_uid: str = Depends(require_verified_tailor),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Add a work portfolio piece to a shop owned by the authenticated tailor."""
    try:
        shop = await use_case.get_shop_by_id(shop_id)
        if shop.tailor_id != authenticated_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this shop.",
            )
        return await use_case.add_shop_work(
            shop_id=shop_id,
            image_url=request.image_url,
            description=request.description,
        )
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete(
    "/{shop_id}/works/{work_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_shop_work(
    shop_id: int,
    work_id: int,
    authenticated_uid: str = Depends(require_verified_tailor),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Delete a shop work piece owned by the authenticated tailor."""
    try:
        shop = await use_case.get_shop_by_id(shop_id)
        if shop.tailor_id != authenticated_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this shop.",
            )
        await use_case.delete_shop_work(shop_id=shop_id, work_id=work_id)
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/{shop_id}/gigs",
    response_model=GigResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_gig(
    shop_id: int,
    request: GigCreateRequest,
    authenticated_uid: str = Depends(require_verified_tailor),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Create a gig for a shop owned by the authenticated tailor."""
    try:
        return await use_case.create_gig(
            shop_id=shop_id,
            tailor_id=authenticated_uid,
            title=request.title,
            description=request.description,
            price=request.price,
            delivery_time=request.delivery_time,
            category=request.category,
            image_url=request.image_url,
        )
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.delete("/gigs/{gig_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gig(
    gig_id: int,
    authenticated_uid: str = Depends(require_verified_tailor),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Delete a gig owned by the authenticated tailor."""
    try:
        await use_case.delete_gig(gig_id=gig_id, tailor_id=authenticated_uid)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
