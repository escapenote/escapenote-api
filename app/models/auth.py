from typing import Optional, Union
from pydantic import BaseModel, Field


class AccessUser(BaseModel):
    provider: Union[str, None] = None
    id: Union[str, None] = None


class Token(BaseModel):
    token_type: str
    access_token: str


class EditProfileDto(BaseModel):
    avatar: Optional[str] = Field("")
    nickname: str
    type: Optional[str] = Field("")


class ChangePasswordDto(BaseModel):
    oldPassword: Optional[str] = Field("")
    newPassword: str


class CheckForDuplicateNicknameDto(BaseModel):
    nickname: str


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
    agreeMarketing: bool


class SignupBySocialDto(BaseModel):
    avatar: Optional[str] = Field("")
    nickname: str
    type: Optional[str] = Field("")
    agreeMarketing: bool


class LoginByEmaileDto(BaseModel):
    email: str
    password: str
