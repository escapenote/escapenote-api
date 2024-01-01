from typing import List, Optional
from pydantic import BaseModel

from prisma import models


class User(BaseModel):
    id: str
    email: Optional[str]
    nickname: str
    avatar: str
    type: str
    hasPassword: Optional[bool] = None
    accounts: Optional[List["models.Account"]]
    cafeReviews: Optional[List["models.CafeReview"]]
    themeReviews: Optional[List["models.ThemeReview"]]
