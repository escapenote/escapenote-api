from pydantic import BaseModel


class CreateCafeReview(BaseModel):
    rating: int
    text: str
