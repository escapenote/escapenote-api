from typing import Optional
from fastapi import APIRouter, Cookie, Response
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.prisma import prisma
from app.models.auth import (
    CheckForDuplicateUsernameDto,
    LoginDto,
    Token,
    CheckForDuplicateEmaileDto,
    SendCodeByEmaileDto,
    SignupByEmaileDto,
    SignupByPhoneDto,
    CheckForDuplicatePhoneDto,
    SendCodeByPhoneDto,
    VerifyCodeByEmaileDto,
    VerifyCodeByPhoneDto,
)
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
    return {"token_type": "bearer", "access_token": tokens["access_token"]}


@router.get("/profile")
async def read_users_me(
    current_user=Depends(auth_service.get_current_user),
):
    user = await prisma.user.find_unique(where={"id": current_user.id})
    return user


@router.post("/phone/duplicate")
async def check_for_duplicate_phone(body: CheckForDuplicatePhoneDto):
    return await auth_service.check_for_duplicate("phoneNumber", body.phoneNumber)


@router.post("/phone/send_code")
async def send_code_by_phone(body: SendCodeByPhoneDto):
    return await auth_service.send_code("phoneNumber", body.phoneNumber)


@router.post("/phone/verify_code")
async def verify_code_by_phone(body: VerifyCodeByPhoneDto):
    return await auth_service.verify_code("phoneNumber", body.phoneNumber, body.code)


@router.post("/phone/signup")
async def signup_by_phone(body: SignupByPhoneDto):
    return await auth_service.signup(
        "phoneNumber",
        body.phoneNumber,
        body.username,
        body.password,
        body.avatar,
        body.code,
    )


@router.post("/email/duplicate")
async def check_for_duplicate_email(body: CheckForDuplicateEmaileDto):
    return await auth_service.check_for_duplicate("email", body.email)


@router.post("/email/send_code")
async def send_code_by_email(body: SendCodeByEmaileDto):
    return await auth_service.send_code("email", body.email)


@router.post("/email/verify_code")
async def verify_code_by_email(body: VerifyCodeByEmaileDto):
    return await auth_service.verify_code("email", body.email, body.code)


@router.post("/email/signup")
async def signup_by_email(body: SignupByEmaileDto):
    return await auth_service.signup(
        "email",
        body.email,
        body.username,
        body.password,
        body.avatar,
        body.code,
    )


@router.post("/login")
async def login(res: Response, body: LoginDto):
    if body.email:
        return await auth_service.login(res, "email", body.email, body.password)
    elif body.phoneNumber:
        return await auth_service.login(
            res, "phoneNumber", body.phoneNumber, body.password
        )
    elif body.username:
        return await auth_service.login(res, "username", body.username, body.password)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not found username, email, phoneNumber",
        )


@router.post("/username/duplicate")
async def check_for_duplicate_username(body: CheckForDuplicateUsernameDto):
    return await auth_service.check_for_duplicate("username", body.username)


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


@router.post("/logout")
async def logout(
    res: Response,
    current_user=Depends(auth_service.get_current_user),
):
    return await auth_service.logout(res, current_user.id)
