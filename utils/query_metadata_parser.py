# utils/query_metadata_parser.py

import re

def get_query_metadata(text: str) -> dict:
    match = re.match(r"(查詢|股價|配息)\s*(\d{4})(?:\s*(\d{8}))?", text)
    if not match:
        return {
            "query_type": None,
            "stock_id": None,
            "date": None,
            "raw": text
        }
    cmd, stock_id, date = match.groups()
    return {
        "query_type": "dividend" if cmd == "配息" else "price",
        "stock_id": stock_id,
        "date": date,
        "raw": text
    }
