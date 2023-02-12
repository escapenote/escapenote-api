from typing import Optional
from pydantic import BaseModel, Field


class UpdateThemeReview(BaseModel):
    rating: int
    success: bool
    level: Optional[int] = Field(0)
    fear: Optional[int] = Field(0)
    activity: Optional[int] = Field(0)
    text: str
