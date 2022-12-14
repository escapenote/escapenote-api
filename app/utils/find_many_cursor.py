from typing import Any, List, Optional


def find_many_cursor(
    items: List[Any], take: Optional[int] = 20, cursor: Optional[bool] = None
):
    if cursor:
        if items:
            end_cursor = items[-1].id
        else:
            end_cursor = None

        start_cursor = items[0].id

        if len(items) > take:
            items.pop()

        if len(items) < take:
            end_cursor = None

        return {
            "pageInfo": {
                "startCursor": start_cursor,
                "endCursor": end_cursor,
            },
            "items": items,
        }
    else:
        if items:
            start_cursor = items[0].id
            end_cursor = items[-1].id
        else:
            start_cursor = None
            end_cursor = None

        if len(items) < take:
            end_cursor = None

        if len(items) > take:
            items.pop()

        return {
            "pageInfo": {
                "startCursor": start_cursor,
                "endCursor": end_cursor,
            },
            "items": items,
        }
