from typing import Optional
from pydantic import BaseModel


class PageInfo(BaseModel):
    startCursor: Optional[str]
    endCursor: Optional[str]
