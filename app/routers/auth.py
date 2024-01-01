import requests
from typing import Optional
from fastapi import APIRouter, Cookie, Response
from fastapi import Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.prisma import prisma
from app.config import settings
from app.models.auth import (
    CheckForDuplicateNicknameDto,
    EditProfileDto,
    LoginByEmaileDto,
    ChangePasswordDto,
    SendPasswordByEmaileDto,
    SignupBySocialDto,
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


@router.get("/profile", response_model=User)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    user = await prisma.user.find_unique(
        where={"id": current_user.id},
    )
    user = auth_utils.check_has_password(user)
    return user


@router.patch("/profile/edit")
async def edit_profile(
    body: EditProfileDto, current_user: User = Depends(auth_service.get_current_user)
):
    return await auth_service.edit_profile(current_user.id, body)


@router.patch("/password/change")
async def change_password(
    body: ChangePasswordDto, current_user: User = Depends(auth_service.get_current_user)
):
    return await auth_service.change_password(current_user.id, body)


@router.post("/nickname/duplicate")
async def check_for_duplicate_nickname(body: CheckForDuplicateNicknameDto):
    return await auth_service.check_for_duplicate_nickname(body.nickname)


@router.post("/email/duplicate")
async def check_for_duplicate_email(body: CheckForDuplicateEmaileDto):
    return await auth_service.check_for_duplicate_email(body.email)


@router.post("/email/send_code")
async def send_code_by_email(body: SendCodeByEmaileDto):
    return await auth_service.send_code_by_email(body.email)


@router.post("/email/verify_code")
async def verify_code_by_email(body: VerifyCodeByEmaileDto):
    return await auth_service.verify_code_by_email(body.email, body.code)


@router.post("/email/send_password")
async def send_password_by_email(body: SendPasswordByEmaileDto):
    return await auth_service.send_password_by_email(body.email)


@router.post("/signup/email")
async def signup_by_email(res: Response, body: SignupByEmaileDto):
    return await auth_service.signup_by_email(res, body)


@router.post("/signup/social")
async def signup_by_social(
    res: Response, body: SignupBySocialDto, registerToken: Optional[str] = Cookie(None)
):
    if registerToken:
        user = await auth_service.get_current_user(registerToken)
        result = await auth_service.signup_by_social(res, user, body)
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="회원가입 권한이 없습니다.",
        )


@router.post("/login/email")
async def login_by_email(res: Response, body: LoginByEmaileDto):
    return await auth_service.login_by_email(res, body.email, body.password)


@router.get("/login/google")
async def login_google():
    client_id = settings.google_client_id
    redirect_uri = f"{settings.backend_url}/auth/callback/google"
    scope = "email%20profile"
    url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
    return RedirectResponse(url)


@router.get("/callback/google")
async def login_google_callback(code: str):
    provider = "google"
    client_id = settings.google_client_id
    client_secret = settings.google_client_secret
    redirect_uri = f"{settings.backend_url}/auth/callback/google"

    # Access Token을 받아옴
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    token_res = requests.post("https://oauth2.googleapis.com/token", data=data)
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    # Access Token을 사용하여 사용자 정보를 받아옴
    if access_token:
        profile_res = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_res.json()
        email = profile_json["email"]

        user = await prisma.user.find_first(where={"email": email})
        if user:
            res = RedirectResponse(settings.front_main_url)
            await auth_service.login_by_social(res, provider, email)
            return res
        else:
            res = RedirectResponse(settings.front_signup_url)
            await auth_service.pre_signup_by_social(res, provider, email)
            return res
    else:
        return {"error": "Could not authenticate"}


@router.get("/login/naver")
async def login_naver():
    client_id = settings.naver_client_id
    redirect_uri = f"{settings.backend_url}/auth/callback/naver"
    url = f"https://nid.naver.com/oauth2.0/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    return RedirectResponse(url)


@router.get("/callback/naver")
async def login_naver_callback(code: str, state: str):
    provider = "naver"
    client_id = settings.naver_client_id
    client_secret = settings.naver_client_secret
    redirect_uri = f"{settings.backend_url}/auth/callback/naver"
    api_url = f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&code={code}&state={state}"

    token_res = requests.get(
        api_url,
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        },
    )
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    profile_res = requests.get(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_res.json()
    profile = profile_json["response"]
    email = profile["email"]

    user = await prisma.user.find_first(where={"email": email})
    if user:
        res = RedirectResponse(settings.front_main_url)
        await auth_service.login_by_social(res, provider, email)
        return res
    else:
        res = RedirectResponse(settings.front_signup_url)
        await auth_service.pre_signup_by_social(res, provider, email)
        return res


@router.get("/login/kakao")
async def login_kakao():
    client_id = settings.kakao_client_id
    redirect_uri = f"{settings.backend_url}/auth/callback/kakao"
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    return RedirectResponse(url)


@router.get("/callback/kakao")
async def login_kakao_callback(code: str):
    provider = "kakao"
    client_id = settings.kakao_client_id
    client_secret = settings.kakao_client_secret
    redirect_uri = f"{settings.backend_url}/auth/callback/kakao"
    api_url = "https://kauth.kakao.com/oauth/token"

    token_res = requests.post(
        api_url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    profile_res = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_res.json()
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account["email"]

    user = await prisma.user.find_first(where={"email": email})
    if user:
        res = RedirectResponse(settings.front_main_url)
        await auth_service.login_by_social(res, provider, email)
        return res
    else:
        res = RedirectResponse(settings.front_signup_url)
        await auth_service.pre_signup_by_social(res, provider, email)
        return res


@router.post("/logout")
async def logout(
    res: Response,
    current_user: User = Depends(auth_service.get_current_user),
):
    return await auth_service.logout(res, current_user.id)
