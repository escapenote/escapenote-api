import uuid
import boto3
from fastapi import APIRouter, File, UploadFile
from fastapi import APIRouter, Depends, Header

from app.config import settings
from app.models.auth import AccessUser
from app.models.user import User
from app.prisma import prisma
from app.services import auth as auth_service


router = APIRouter(
    prefix="/images",
    tags=["images"],
    responses={404: {"description": "Not found"}},
)


@router.post("/user")
async def upload_image(file: UploadFile = File(None)):
    """
    사용자 이미지 업로드
    """
    ### AWS 세팅
    session = boto3.Session()
    s3 = session.resource("s3")
    bucket_name = "escapenote-images"
    folder_name = "users"
    bucket = s3.Bucket(bucket_name)

    try:
        filename = uuid.uuid1()
        type = "jpeg"
        key = f"{folder_name}/{filename}.{type}"
        bucket.upload_fileobj(
            file.file,
            key,
            ExtraArgs={
                "ContentType": f"image/{type}",
                "CacheControl": "max-age=172800",
            },
        )
        return {"url": f"/{key}"}
    except Exception as e:
        print("error", e)
        return None
