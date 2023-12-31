from typing import List, Optional
from pydantic import BaseModel

from prisma import models


class User(BaseModel):
    id: str
    email: Optional[str]
    avatar: str
    nickname: str
    type: str
    hasPassword: Optional[bool]
    accounts: Optional[List["models.Account"]]
    cafeReviews: Optional[List["models.CafeReview"]]
    themeReviews: Optional[List["models.ThemeReview"]]
