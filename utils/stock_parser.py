# utils/stock_parser.py

import re
from modules.stock_mapping_service import StockNameResolver

resolver = StockNameResolver()

def extract_stock_id(text: str) -> str | None:
    match = re.search(r"\d{4}", text)
    if match:
        return match.group()
    return resolver.get_stock_id(text)

def normalize_query_type(text: str) -> str:
    """將原始查詢文字轉換為標準查詢類型（dividend, yield, policy）"""
    text = text.lower()
    if any(kw in text for kw in ["殖利率", "yield", "報酬率", "年化"]):
        return "yield"
    if any(kw in text for kw in ["股利政策", "配息策略", "政策", "股利發放"]):
        return "policy"
    if any(kw in text for kw in ["配息", "除息", "股息", "現金股利", "除權"]):
        return "dividend"
    return "unknown"

