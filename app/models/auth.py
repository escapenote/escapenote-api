from typing import Optional, Union
from pydantic import BaseModel, Field


class AccessUser(BaseModel):
    id: Union[str, None] = None


class Token(BaseModel):
    token_type: str
    access_token: str


class EditProfileDto(BaseModel):
    avatar: Optional[str] = Field("")
    nickname: str
    type: Optional[str] = Field("")


class ChangePasswordDto(BaseModel):
    oldPassword: str
    newPassword: str


class SendPasswordByEmaileDto(BaseModel):
    email: str


class CheckForDuplicateEmaileDto(BaseModel):
    email: str


class SendCodeByEmaileDto(BaseModel):
    email: str


class VerifyCodeByEmaileDto(BaseModel):
    email: str
    code: str


class SignupByEmaileDto(BaseModel):
    email: str
    password: str
    code: str
    avatar: Optional[str] = Field("")
    nickname: str
    type: Optional[str] = Field("")
    agreeOlder14Years: bool
    agreeTerms: bool
    agreePrivacy: bool
    agreeMarketing: bool


class LoginDto(BaseModel):
    email: str
    password: str


class CheckForDuplicateNicknameDto(BaseModel):
    nickname: str
