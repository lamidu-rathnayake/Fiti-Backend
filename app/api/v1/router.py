from fastapi import APIRouter

from app.api.v1.endpoints import health, orders, profiles, rbac, shops, support

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(profiles.router)
api_v1_router.include_router(shops.router)
api_v1_router.include_router(orders.router)
api_v1_router.include_router(rbac.router)
api_v1_router.include_router(support.router)
