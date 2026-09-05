import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


def validate_email_str(v: str) -> str:
    if not EMAIL_REGEX.match(v):
        raise ValueError("Invalid email address format.")
    return v


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def email_validator(cls, v: str) -> str:
        return validate_email_str(v)


class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v: str) -> str:
        return validate_email_str(v)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserProfileUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None

    @field_validator("email")
    @classmethod
    def email_validator(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_email_str(v)
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes


class UserDetailResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    roles: List[str]
    permissions: List[str]
