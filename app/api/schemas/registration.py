from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class ActivateRequest(BaseModel):
    code: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
