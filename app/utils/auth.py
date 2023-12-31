import boto3
import secrets
import string
from jose import jwt
from random import randint
from typing import Union, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.config import settings

# to get a string like this run: openssl rand -hex 32
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30
REGISTER_TOKEN_EXPIRE_DAY = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_code():
    n = 6
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return str(randint(range_start, range_end))


def generate_password():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation

    alphabet = letters + digits + special_chars

    # fix password length
    pwd_length = 12

    # generate a password string
    pwd = ""
    for i in range(pwd_length):
        pwd += "".join(secrets.choice(alphabet))

    return pwd


def send_secret_by_email(address: str, secret: str):
    try:
        ses = boto3.client("ses")
        response = ses.send_email(
            Source="no-reply@escape-note.com",
            Destination={
                "ToAddresses": [address],
            },
            Message={
                "Subject": {
                    "Charset": "utf-8",
                    "Data": "이스케이프노트의 인증번호입니다.",
                },
                "Body": {
                    "Html": {
                        "Charset": "utf-8",
                        "Data": f"이스케이프노트의 인증번호는 [<strong>{secret}</strong>] 입니다.",
                    }
                },
            },
        )
        return response
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이메일을 보내지 못했습니다.",
        )


def send_password_by_email(address: str, password: str):
    try:
        ses = boto3.client("ses")
        response = ses.send_email(
            Source="no-reply@escape-note.com",
            Destination={
                "ToAddresses": [address],
            },
            Message={
                "Subject": {
                    "Charset": "utf-8",
                    "Data": "이스케이프노트 임시 비밀번호입니다.",
                },
                "Body": {
                    "Html": {
                        "Charset": "utf-8",
                        "Data": f"이스케이프노트 임시 비밀번호는 <strong>{password}</strong> 입니다.",
                    }
                },
            },
        )
        return response
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이메일을 보내지 못했습니다.",
        )


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_tokens(userId: str):
    jwt_payload = {"sub": userId}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(data=jwt_payload, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_token(data=jwt_payload, expires_delta=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def generate_register_token(provider: str, email: str):
    jwt_payload = {"provider": provider, "sub": email}

    register_token_expires = timedelta(days=REGISTER_TOKEN_EXPIRE_DAY)
    register_token = create_token(
        data=jwt_payload, expires_delta=register_token_expires
    )

    return {
        "register_token": register_token,
    }


def check_has_password(user: Any):
    user = user.__dict__
    if user["password"]:
        user["hasPassword"] = True
    else:
        user["hasPassword"] = False
    return user
