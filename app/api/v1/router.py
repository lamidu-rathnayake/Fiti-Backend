from fastapi import APIRouter
from app.api.v1.endpoints import health, users, shops, orders

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(shops.router)
api_v1_router.include_router(orders.router)
