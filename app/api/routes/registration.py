from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps.mailer import get_mailer
from app.api.deps.repository import get_activation_code_repository, get_user_repository
from app.api.schemas.registration import RegisterRequest, ActivateRequest
from app.api.deps.auth import get_authenticated_user
from app.domain.exceptions import (
    UserAlreadyExists,
    ActivationCodeExpired,
    ActivationCodeInvalid,
    UserAlreadyActive,
    ActivationCodeLocked,
)
from app.domain.models.user import User
from app.domain.models.activation_code import ActivationCode
from app.domain.services.registration_service import RegistrationService
from app.infrastructure.repositories.user_repository import PostgresUserRepository
from app.infrastructure.repositories.activation_code_repository import PostgresActivationCodeRepository
from app.infrastructure.mailer.console_mailer import ConsoleMailer
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="", tags=["registration"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    user_repo=Depends(get_user_repository),
    activation_code_repo=Depends(get_activation_code_repository),
    mailer=Depends(get_mailer)
):
    service = RegistrationService(user_repo, activation_code_repo, mailer)

    user = User.create(payload.email, payload.password)

    try:
        await service.register(user)
    except UserAlreadyExists:
        logger.info("Registration attempt for existing user: %s", user.email)
        #We purposedly don't reply 409 or else to prevent user enumeration vulnerability

    return {"status": "ok"}


@router.post("/activate", status_code=status.HTTP_200_OK)
async def activate(
    payload: ActivateRequest,
    user=Depends(get_authenticated_user),
    user_repo=Depends(get_user_repository),
    activation_code_repo=Depends(get_activation_code_repository),
):
    service = RegistrationService(
        user_repo=user_repo,
        activation_code_repo=activation_code_repo,
        mailer=None, 
    )
    code = await activation_code_repo.get_for_user(user.id)

    try:
        await service.activate(
            user=user,
            activation_code=code,
            provided_code=payload.code,
            now = datetime.now(timezone.utc),
        )
    except (
        ActivationCodeExpired,
        ActivationCodeInvalid,
        ActivationCodeLocked,
        UserAlreadyActive,
    ):
        # neutral reply - no info leak
        pass

    return {"status": "processed"}
