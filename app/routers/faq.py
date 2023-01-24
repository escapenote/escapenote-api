from typing import Optional
from prisma import types
from fastapi import APIRouter

from app.prisma import prisma


router = APIRouter(
    prefix="/faq",
    tags=["faq"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_faq_list(
    term: Optional[str] = None,
    sort: Optional[str] = "position",
    order: Optional[str] = "asc",
):
    options: types.FindManyFaqArgsFromFaq = {
        "where": {"status": "PUBLISHED"},
        "order": {sort: order},
    }
    if term:
        options["where"]["question"] = {"contains": term}

    faq_list = await prisma.faq.find_many(**options)
    return faq_list
