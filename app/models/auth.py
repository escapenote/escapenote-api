from typing import Optional, Union
from fastapi import File, UploadFile
from pydantic import BaseModel, Field


class AccessUser(BaseModel):
    id: Union[str, None] = None


class Token(BaseModel):
    token_type: str
    access_token: str


class EditProfileDto(BaseModel):
    imageFile: UploadFile = File(None)
    username: Optional[str]
    headline: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    instagram: Optional[str]


class CheckForDuplicatePhoneDto(BaseModel):
    phoneNumber: str


class SendCodeByPhoneDto(BaseModel):
    phoneNumber: str


class VerifyCodeByPhoneDto(BaseModel):
    phoneNumber: str
    code: str


class SignupByPhoneDto(BaseModel):
    avatar: Optional[str]
    username: str
    phoneNumber: str
    password: str
    code: str


class CheckForDuplicateEmaileDto(BaseModel):
    email: str


class SendCodeByEmaileDto(BaseModel):
    email: str


class VerifyCodeByEmaileDto(BaseModel):
    email: str
    code: str


class SignupByEmaileDto(BaseModel):
    avatar: Optional[str] = Field("")
    username: str
    email: str
    password: str
    code: str


class LoginDto(BaseModel):
    email: Optional[str]
    phoneNumber: Optional[str]
    username: Optional[str]
    password: str


class CheckForDuplicateUsernameDto(BaseModel):
    username: str
