from pydantic import BaseModel


class UpdateCafeReview(BaseModel):
    rating: int
    text: str
