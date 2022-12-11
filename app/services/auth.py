from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer

from app.prisma import prisma
from app.config import settings
from app.models.auth import AccessUser
from app.utils import auth as auth_utils

DOMAIN = "localhost" if settings.app_env == "local" else ".escape-note.com"
REFRESH_TOKEN_EXPIRE_IN = 3600 * 24 * 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def authenticate_user(username: str, password: str):
    user = await prisma.user.find_unique(where={"username": username})
    if not user:
        return False
    if not auth_utils.verify_password(password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
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


async def check_for_duplicate(type: str, value: str):
    options = dict()
    if type == "email":
        options["where"] = {"email": value}
    elif type == "phoneNumber":
        options["where"] = {"phoneNumber": value}
    else:
        options["where"] = {"username": value}
    user = await prisma.user.find_unique(**options)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{type} is duplicated",
        )
    return True


async def send_code(type: str, value: str):
    where = dict()
    if type == "email":
        where["email"] = value
    else:
        where["phoneNumber"] = value
    user = await prisma.user.find_unique(where=where)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"this {type} is already in use.",
        )

    await prisma.cert.update_many(
        where={
            "type": "EMAIL" if type == "email" else "PHONE_NUMBER",
            "value": value,
            "status": "PENDING",
        },
        data={"status": "INVALID"},
    )

    secret = auth_utils.generate_secret()
    await prisma.cert.create(
        data={
            "type": "EMAIL" if type == "email" else "PHONE_NUMBER",
            "value": value,
            "status": "PENDING",
            "secret": secret,
        }
    )

    if type == "email":
        auth_utils.send_secret_by_email(value, secret)
    else:
        auth_utils.send_secret_by_phone(value, secret)

    return True


async def verify_code(type: str, value: str, code: str):
    cert = await prisma.cert.find_first(
        where={
            "type": "EMAIL" if type == "email" else "PHONE_NUMBER",
            "value": value,
            "status": "PENDING",
        }
    )

    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="not have a certficate",
        )

    if cert.secret != code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"wrong {type}/code combination",
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
    type: str,
    value: str,
    username: str,
    password: str,
    avatar: str,
    code: str,
):
    cert = await prisma.cert.find_first(
        where={
            "type": "EMAIL" if type == "email" else "PHONE_NUMBER",
            "value": value,
            "status": "VERIFIED",
        }
    )
    if cert.secret != code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"wrong {type}/code combination",
        )

    user_where = dict()
    if type == "email":
        user_where["email"] = value
    else:
        user_where["phoneNumber"] = value
    user = await prisma.user.find_unique(where=user_where)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"duplicate {type}",
        )

    user = await prisma.user.find_unique(where={"username": username})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="duplicate username",
        )

    hashed_password = auth_utils.get_password_hash(password)
    data = {
        "username": username,
        "password": hashed_password,
        "avatar": avatar,
    }
    if type == "email":
        data["email"] = value
        data["emailVerified"] = True
    else:
        data["phoneNumber"] = value
        data["phoneNumberVerified"] = True
    user = await prisma.user.create(data=data)

    await prisma.cert.update(
        where={"id": cert.id},
        data={"status": "COMPLETE"},
    )

    return user


async def login(
    res: Response,
    type: str,
    value: str,
    password: str,
):
    where = dict()
    if type == "email":
        where["email"] = value
    elif type == "phoneNumber":
        where["phoneNumber"] = value
    else:
        where["username"] = value
    user = await prisma.user.find_unique(where=where)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="not found user",
        )

    valid_password = auth_utils.verify_password(
        password,
        user.password,
    )
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid password",
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
            detail="invalid user",
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


async def logout(res: Response, userId: str):
    res.delete_cookie("refreshToken")

    await prisma.user.update_many(
        where={
            "id": userId,
            "refreshToken": {
                "not": None,
            },
        },
        data={
            "refreshToken": None,
        },
    )
    return True
