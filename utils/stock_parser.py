# utils/stock_parser.py

import re

from modules.stock_mapping_service import StockNameResolver

resolver = StockNameResolver()
def extract_stock_id(text: str) -> str | None:
    match = re.search(r"\d{4}", text)
    if match:
        return match.group()
    return resolver.get_stock_id(text)

