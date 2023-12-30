from datetime import datetime
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
    SignupBySocialDto,
)
from app.utils import auth as auth_utils

ACCESS_TOKEN_EXPIRE_IN = 3600  # 1 hour
REFRESH_TOKEN_EXPIRE_IN = 3600 * 24 * 30  # 1 month
REGISTER_TOKEN_EXPIRE_IN = 3600 * 24  # 1 day

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
        provider: str = payload.get("provider")
        userId: str = payload.get("sub")
        if userId is None:
            raise credentials_exception
        user = AccessUser(id=userId, provider=provider)
        return user
    except JWTError:
        raise credentials_exception


async def refresh(res: Response, user: AccessUser):
    if not user:
        res.delete_cookie(key="refreshToken", domain=settings.domain, path="/")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="접근 권한이 없습니다.",
        )

    tokens = auth_utils.generate_tokens(user.id)
    res.set_cookie(
        key="refreshToken",
        value=tokens["refresh_token"],
        domain=settings.domain,
        path="/",
        expires=REFRESH_TOKEN_EXPIRE_IN,
        httponly=True,
        secure=False,
    )

    user = await prisma.user.update(
        where={"id": user.id},
        data={"refreshToken": tokens["refresh_token"]},
    )
    user = user.__dict__
    if user["password"]:
        user["hasPassword"] = True
    else:
        user["hasPassword"] = False

    return {
        "tokenType": "bearer",
        "accessToken": tokens["access_token"],
        "refreshToken": tokens["refresh_token"],
        "expiredAt": REFRESH_TOKEN_EXPIRE_IN,
        "user": user,
    }


async def edit_profile(user_id: str, body: EditProfileDto):
    user = await prisma.user.update(
        where={"id": user_id},
        data={
            **body.dict(exclude_none=True),
        },
    )
    return user


async def change_password(user_id: str, body: ChangePasswordDto):
    user = await prisma.user.find_unique(
        where={"id": user_id},
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    # 이메일로 가입한 사용자만 현재 비밀번호 체크 후 변경
    if not user.password:
        if not body.oldPassword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="현재 비밀번호를 입력해주세요.",
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


async def check_for_duplicate_email(email: str):
    user = await prisma.user.find_unique(where={"email": email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"이메일이 중복되었습니다.",
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

    await prisma.verificationcode.update_many(
        where={
            "identifier": email,
            "status": "PENDING",
        },
        data={"status": "INVALID"},
    )

    code = auth_utils.generate_code()
    await prisma.verificationcode.create(
        data={
            "identifier": email,
            "code": code,
            "status": "PENDING",
        }
    )

    auth_utils.send_secret_by_email(email, code)

    return True


async def verify_code(email: str, code: str):
    await prisma.verificationcode.update_many(
        where={
            "identifier": email,
            "status": "VERIFIED",
        },
        data={"status": "INVALID"},
    )

    verification_code = await prisma.verificationcode.find_first(
        where={
            "identifier": email,
            "status": "PENDING",
        }
    )

    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="인증 자격이 없습니다.",
        )

    if verification_code.code != code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"잘못된 이메일/코드 조합입니다.",
        )

    try:
        await prisma.verificationcode.update(
            where={"id": verification_code.id},
            data={"status": "VERIFIED"},
        )
        return True
    except:
        return False


async def login_by_email(res: Response, email: str, password: str):
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
        domain=settings.domain,
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
        "expiredAt": REFRESH_TOKEN_EXPIRE_IN,
        "user": user,
    }


async def signup_by_email(res: Response, body: SignupByEmaileDto):
    verification_code = await prisma.verificationcode.find_first(
        where={
            "identifier": body.email,
            "status": "VERIFIED",
        }
    )
    if verification_code.code != body.code:
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
            "agreeOlder14Years": True,
            "agreeTerms": True,
            "agreePrivacy": True,
            "agreeMarketing": body.agreeMarketing,
        }
    )

    await prisma.verificationcode.update(
        where={"id": verification_code.id},
        data={"status": "COMPLETE"},
    )

    tokens = auth_utils.generate_tokens(user.id)
    res.set_cookie(
        key="refreshToken",
        value=tokens["refresh_token"],
        domain=settings.domain,
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
        "expiredAt": REFRESH_TOKEN_EXPIRE_IN,
        "user": user,
    }


async def login_by_social(res: Response, provider: str, email: str):
    user = await prisma.user.find_first(
        where={"email": email},
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    account = await prisma.account.find_first(
        where={
            "provider": provider,
            "userId": user.id,
        }
    )
    if not account:
        await prisma.account.create(
            data={
                "provider": provider,
                "userId": user.id,
            }
        )

    tokens = auth_utils.generate_tokens(user.id)
    res.set_cookie(
        key="refreshToken",
        value=tokens["refresh_token"],
        domain=settings.domain,
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


async def pre_signup_by_social(res: Response, provider: str, email: str):
    tokens = auth_utils.generate_register_token(provider, email)
    res.set_cookie(
        key="registerToken",
        value=tokens["register_token"],
        domain=settings.domain,
        path="/",
        expires=REGISTER_TOKEN_EXPIRE_IN,
        httponly=True,
        secure=False,
    )

    return {
        "tokenType": "bearer",
        "registerToken": tokens["register_token"],
        "provider": provider,
        "email": email,
    }


async def signup_by_social(
    res: Response, access_user: AccessUser, body: SignupBySocialDto
):
    user = await prisma.user.find_unique(where={"email": access_user.id})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"이미 사용중인 이메일입니다.",
        )

    user = await prisma.user.find_unique(where={"nickname": body.nickname})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"이미 사용중인 닉네임입니다.",
        )

    create_user = await prisma.user.create(
        data={
            "email": access_user.id,
            "avatar": body.avatar,
            "nickname": body.nickname,
            "type": body.type,
            "agreeOlder14Years": True,
            "agreeTerms": True,
            "agreePrivacy": True,
            "agreeMarketing": body.agreeMarketing,
        }
    )
    await prisma.account.create(
        data={
            "provider": access_user.provider,
            "userId": create_user.id,
        }
    )

    tokens = auth_utils.generate_tokens(create_user.id)
    res.delete_cookie(key="registerToken", domain=settings.domain, path="/")
    res.set_cookie(
        key="refreshToken",
        value=tokens["refresh_token"],
        domain=settings.domain,
        path="/",
        expires=REFRESH_TOKEN_EXPIRE_IN,
        httponly=True,
        secure=False,
    )

    current_user = await prisma.user.update(
        where={"id": create_user.id},
        data={"refreshToken": tokens["refresh_token"]},
    )

    return {
        "tokenType": "bearer",
        "accessToken": tokens["access_token"],
        "refreshToken": tokens["refresh_token"],
        "user": current_user,
    }


async def logout(res: Response, userId: str):
    res.delete_cookie(key="refreshToken", domain=settings.domain, path="/")

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
