# app/api/deps/repositories.py
from fastapi import Depends
from app.api.deps.db import get_db_pool
from app.infrastructure.repositories.user_repository import PostgresUserRepository
from app.infrastructure.repositories.activation_code_repository import PostgresActivationCodeRepository

def get_user_repository(pool=Depends(get_db_pool)):
    return PostgresUserRepository(pool)

def get_activation_code_repository(pool=Depends(get_db_pool)):
    return PostgresActivationCodeRepository(pool)
