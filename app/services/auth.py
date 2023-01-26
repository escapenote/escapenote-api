from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer

from app.prisma import prisma
from app.config import settings
from app.models.auth import (
    AccessUser,
    EditProfileDto,
    ChangePasswordDto,
    SignupByEmaileDto,
)
from app.utils import auth as auth_utils

DOMAIN = "localhost" if settings.app_env == "local" else ".escape-note.com"
REFRESH_TOKEN_EXPIRE_IN = 3600 * 24 * 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def authenticate_user(email: str, password: str):
    user = await prisma.user.find_unique(where={"email": email})
    if not user:
        return False
    if not auth_utils.verify_password(password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="자격증명을 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, auth_utils.SECRET_KEY, algorithms=[auth_utils.ALGORITHM]
        )
        userId: str = payload.get("sub")
        if userId is None:
            raise credentials_exception
        user = AccessUser(id=userId)
        return user
    except JWTError:
        raise credentials_exception


async def edit_profile(user_id: str, body: EditProfileDto):
    user = await prisma.user.update(
        where={"id": user_id},
        data={
            **body.dict(exclude_none=True),
        },
    )
    return user


async def change_password(user_id: str, body: ChangePasswordDto):
    user = await prisma.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    valid_password = auth_utils.verify_password(
        body.oldPassword,
        user.password,
    )
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 비밀번호입니다.",
        )

    hashed_password = auth_utils.get_password_hash(body.newPassword)
    user = await prisma.user.update(
        where={"id": user_id},
        data={"password": hashed_password},
    )

    return user


async def check_for_duplicate_email(email: str):
    user = await prisma.user.find_unique(where={"email": email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"이메일이 중복되었습니다.",
        )
    return True


async def check_for_duplicate_nickname(nickname: str):
    with open("app/data/not_allow_nickname.txt") as f:
        lines = f.read().splitlines()
        if nickname in lines:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"사용할 수 없는 닉네임입니다.",
            )

    user = await prisma.user.find_unique(where={"nickname": nickname})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"닉네임이 중복되었습니다.",
        )
    return True


async def send_password(email: str):
    user = await prisma.user.find_unique(where={"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    password = auth_utils.generate_password()
    hashed_password = auth_utils.get_password_hash(password)

    await prisma.user.update(
        where={"email": email},
        data={"password": hashed_password},
    )

    auth_utils.send_password_by_email(email, password)

    return True


async def send_code(email: str):
    user = await prisma.user.find_unique(where={"email": email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"이 이메일은 이미 사용 중입니다.",
        )

    await prisma.cert.update_many(
        where={
            "type": "EMAIL",
            "value": email,
            "status": "PENDING",
        },
        data={"status": "INVALID"},
    )

    secret = auth_utils.generate_secret()
    await prisma.cert.create(
        data={
            "type": "EMAIL",
            "value": email,
            "status": "PENDING",
            "secret": secret,
        }
    )

    auth_utils.send_secret_by_email(email, secret)

    return True


async def verify_code(email: str, code: str):
    await prisma.cert.update_many(
        where={
            "type": "EMAIL",
            "value": email,
            "status": "VERIFIED",
        },
        data={"status": "INVALID"},
    )

    cert = await prisma.cert.find_first(
        where={
            "type": "EMAIL",
            "value": email,
            "status": "PENDING",
        }
    )

    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="인증 자격이 없습니다.",
        )

    if cert.secret != code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"잘못된 이메일/코드 조합입니다.",
        )

    try:
        await prisma.cert.update(
            where={"id": cert.id},
            data={"status": "VERIFIED"},
        )
        return True
    except:
        return False


async def signup(
    res: Response,
    body: SignupByEmaileDto,
):
    cert = await prisma.cert.find_first(
        where={
            "type": "EMAIL",
            "value": body.email,
            "status": "VERIFIED",
        }
    )
    if cert.secret != body.code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"잘못된 이메일/코드 조합입니다.",
        )

    user = await prisma.user.find_unique(where={"email": body.email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"이메일이 중복되었습니다.",
        )

    user = await prisma.user.find_unique(where={"nickname": body.nickname})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="닉네임이 중복되었습니다.",
        )

    hashed_password = auth_utils.get_password_hash(body.password)
    user = await prisma.user.create(
        data={
            "email": body.email,
            "emailVerified": True,
            "password": hashed_password,
            "avatar": body.avatar,
            "nickname": body.nickname,
            "type": body.type,
            "agreeOlder14Years": body.agreeOlder14Years,
            "agreeTerms": body.agreeTerms,
            "agreePrivacy": body.agreePrivacy,
            "agreeMarketing": body.agreeMarketing,
        }
    )

    await prisma.cert.update(
        where={"id": cert.id},
        data={"status": "COMPLETE"},
    )

    tokens = auth_utils.generate_tokens(user.id)
    res.set_cookie(
        key="refreshToken",
        value=tokens["refresh_token"],
        domain=DOMAIN,
        expires=REFRESH_TOKEN_EXPIRE_IN,
        httponly=True,
        secure=False,
    )

    user = await prisma.user.update(
        where={"id": user.id},
        data={"refreshToken": tokens["refresh_token"]},
    )

    return {
        "tokenType": "bearer",
        "accessToken": tokens["access_token"],
        "refreshToken": tokens["refresh_token"],
        "user": user,
    }


async def login(
    res: Response,
    email: str,
    password: str,
):
    user = await prisma.user.find_unique(where={"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    valid_password = auth_utils.verify_password(
        password,
        user.password,
    )
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 비밀번호입니다.",
        )

    tokens = auth_utils.generate_tokens(user.id)
    res.set_cookie(
        key="refreshToken",
        value=tokens["refresh_token"],
        domain=DOMAIN,
        expires=REFRESH_TOKEN_EXPIRE_IN,
        httponly=True,
        secure=False,
    )

    user = await prisma.user.update(
        where={"id": user.id},
        data={"refreshToken": tokens["refresh_token"]},
    )

    return {
        "tokenType": "bearer",
        "accessToken": tokens["access_token"],
        "refreshToken": tokens["refresh_token"],
        "user": user,
    }


async def refresh(res: Response, user: AccessUser):
    if not user:
        res.delete_cookie("refreshToken")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="접근 권한이 없습니다.",
        )

    tokens = auth_utils.generate_tokens(user.id)
    res.set_cookie(
        key="refreshToken",
        value=tokens["refresh_token"],
        domain=DOMAIN,
        path="/",
        expires=REFRESH_TOKEN_EXPIRE_IN,
        httponly=True,
        secure=False,
    )

    user = await prisma.user.update(
        where={"id": user.id},
        data={"refreshToken": tokens["refresh_token"]},
    )

    return {
        "tokenType": "bearer",
        "accessToken": tokens["access_token"],
        "refreshToken": tokens["refresh_token"],
        "user": user,
    }


async def logout(res: Response, userId: str):
    res.delete_cookie(key="refreshToken", domain=DOMAIN, path="/")

    await prisma.user.update_many(
        where={
            "id": userId,
            "refreshToken": {
                "not": "",
            },
        },
        data={
            "refreshToken": "",
        },
    )
    return True
