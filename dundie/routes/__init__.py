from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .transaction import router as transaction_router

main_router = APIRouter()

main_router.include_router(auth_router, tags=["auth"])
main_router.include_router(user_router, prefix="/user", tags=["user"])
main_router.include_router(transaction_router, prefix="/transaction", tags=["transaction"])
