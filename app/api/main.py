from fastapi import APIRouter

from app.api.routes import auth_routes, user_routes

api_router = APIRouter()


api_router.include_router(user_routes.router)
api_router.include_router(auth_routes.router)
