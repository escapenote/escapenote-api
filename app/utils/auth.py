import boto3
from jose import jwt
from random import randint
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Union

# to get a string like this run: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_secret():
    n = 6
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return str(randint(range_start, range_end))


def send_secret_by_email(address: str, secret: str):
    ses = boto3.client("ses")
    response = ses.send_email(
        Source="no-reply@escape-note.com",
        Destination={
            "ToAddresses": [address],
        },
        Message={
            "Subject": {
                "Charset": "utf-8",
                "Data": "Your Escapenote verification code",
            },
            "Body": {
                "Html": {
                    "Charset": "utf-8",
                    "Data": f"Your Escapenote verification code is <strong>{secret}</strong>.",
                }
            },
        },
    )
    return response


def send_secret_by_phone(phoneNumber: str, secret: str):
    sns = boto3.client("sns", region_name="us-east-1")
    response = sns.publish(
        PhoneNumber=phoneNumber,
        Message=f"Your Escapenote verification code is {secret}.",
    )
    return response


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
