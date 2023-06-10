from typing import List, Optional
from pydantic import BaseModel

from prisma import models


class User(BaseModel):
    id: str
    email: Optional[str]
    avatar: str
    nickname: str
    type: str
    cafeReviews: Optional[List["models.CafeReview"]]
    themeReviews: Optional[List["models.ThemeReview"]]
