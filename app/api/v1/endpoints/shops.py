
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_manage_shop_use_case
from app.api.schemas.shop_schema import (
    ShopCreateRequest,
    ShopImageSchema,
    ShopResponse,
    ShopUpdateRequest,
)
from app.domain.exceptions.shop import ShopNotFoundError
from app.use_cases.dtos.shop_dto import ShopCreateDTO, ShopUpdateDTO
from app.use_cases.shop.manage_shop import ManageShopUseCase

router = APIRouter(prefix="/shops", tags=["Shops"])


@router.post("/", response_model=ShopResponse, status_code=status.HTTP_201_CREATED)
async def create_shop(
    request: ShopCreateRequest,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    dto = ShopCreateDTO(
        seller_id=request.seller_id,
        shop_name=request.shop_name,
        shop_bio=request.shop_bio,
        shop_address=request.shop_address,
        city=request.city,
        contact_number=request.contact_number,
        registration_number=request.registration_number,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    return await use_case.create_shop(dto)


@router.get("/nearby", response_model=list[ShopResponse])
async def search_near_shops(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(10.0, description="Search radius in kilometers"),
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Find tailor shops within a GPS radius."""
    return await use_case.search_near_location(lat=lat, lng=lng, radius_km=radius_km)


@router.get("/seller/{seller_id}", response_model=list[ShopResponse])
async def get_shops_by_seller(
    seller_id: str,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Get all shops owned by a specific seller."""
    return await use_case.get_shops_by_seller(seller_id)


@router.get("/{shop_id}", response_model=ShopResponse)
async def get_shop(
    shop_id: int,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    try:
        return await use_case.get_shop_by_id(shop_id)
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/", response_model=list[ShopResponse])
async def list_shops(
    skip: int = 0,
    limit: int = 100,
    city: str | None = None,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    return await use_case.list_shops(skip=skip, limit=limit, city=city)


@router.put("/{shop_id}", response_model=ShopResponse)
async def update_shop(
    shop_id: int,
    request: ShopUpdateRequest,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Update shop details."""
    try:
        dto = ShopUpdateDTO(
            shop_id=shop_id,
            shop_name=request.shop_name,
            shop_bio=request.shop_bio,
            shop_address=request.shop_address,
            city=request.city,
            contact_number=request.contact_number,
            registration_number=request.registration_number,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        return await use_case.update_shop(dto)
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shop(
    shop_id: int,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    """Delete a shop."""
    try:
        await use_case.delete_shop(shop_id)
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/{shop_id}/images", response_model=ShopImageSchema, status_code=status.HTTP_201_CREATED)
async def add_shop_image(
    shop_id: int,
    image_url: str,
    use_case: ManageShopUseCase = Depends(get_manage_shop_use_case),
):
    try:
        return await use_case.add_shop_image(shop_id=shop_id, image_url=image_url)
    except ShopNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
