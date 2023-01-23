from typing import Optional
from fastapi import APIRouter, Cookie, Response
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.prisma import prisma
from app.models.auth import (
    CheckForDuplicateNicknameDto,
    EditProfileDto,
    LoginDto,
    ResetPasswordDto,
    SendPasswordByEmaileDto,
    Token,
    CheckForDuplicateEmaileDto,
    SendCodeByEmaileDto,
    SignupByEmaileDto,
    VerifyCodeByEmaileDto,
)
from app.models.user import User
from app.services import auth as auth_service
from app.utils import auth as auth_utils

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    tokens = auth_utils.generate_tokens(user.id)
    return {"tokenType": "bearer", "accessToken": tokens["access_token"]}


@router.get("/profile", response_model=User)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user),
):
    user = await prisma.user.find_unique(where={"id": current_user.id})
    return user


@router.patch("/profile/edit")
async def edit_profile(
    body: EditProfileDto, current_user: User = Depends(auth_service.get_current_user)
):
    return await auth_service.edit_profile(current_user.id, body)


@router.patch("/password/reset")
async def reset_password(
    body: ResetPasswordDto, current_user: User = Depends(auth_service.get_current_user)
):
    return await auth_service.reset_password(current_user.id, body)


@router.post("/email/send_password")
async def send_password_by_email(body: SendPasswordByEmaileDto):
    return await auth_service.send_password(body.email)


@router.post("/email/duplicate")
async def check_for_duplicate_email(body: CheckForDuplicateEmaileDto):
    return await auth_service.check_for_duplicate_email(body.email)


@router.post("/email/send_code")
async def send_code_by_email(body: SendCodeByEmaileDto):
    return await auth_service.send_code(body.email)


@router.post("/email/verify_code")
async def verify_code_by_email(body: VerifyCodeByEmaileDto):
    return await auth_service.verify_code(body.email, body.code)


@router.post("/email/signup")
async def signup_by_email(res: Response, body: SignupByEmaileDto):
    return await auth_service.signup(res, body)


@router.post("/nickname/duplicate")
async def check_for_duplicate_nickname(body: CheckForDuplicateNicknameDto):
    return await auth_service.check_for_duplicate_nickname(body.nickname)


@router.post("/refresh")
async def refresh(res: Response, refreshToken: Optional[str] = Cookie(None)):
    if refreshToken:
        user = await auth_service.get_current_user(refreshToken)
        return await auth_service.refresh(res, user)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="not found refresh token",
        )


@router.post("/login")
async def login(res: Response, body: LoginDto):
    return await auth_service.login(res, body.email, body.password)


@router.post("/logout")
async def logout(
    res: Response,
    current_user: User = Depends(auth_service.get_current_user),
):
    return await auth_service.logout(res, current_user.id)
