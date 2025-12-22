from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.api.deps.repository import get_user_repository
from app.utils.security import verify_password

security = HTTPBasic()


async def get_authenticated_user(
    credentials: HTTPBasicCredentials = Depends(security),
    user_repo=Depends(get_user_repository),
):
    user = await user_repo.get_by_email(credentials.username)

    if not user or not verify_password(user.password_hash, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user
