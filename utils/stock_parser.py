# utils/stock_parser.py

import re
from modules.stock_mapping_service import StockNameResolver

def extract_ex_date_from_note(note: str) -> str | None:
    import re

    # 1. 國曆格式（如 1140725）
    match = re.search(r"除[權息]?交易日(?:為)?[:：]?\s*(\d{3})(\d{2})(\d{2})", note)
    if match:
        year = str(1911 + int(match.group(1)))
        return f"{year}/{match.group(2)}/{match.group(3)}"

    # 2. 一般格式（2025/07/25）
    match = re.search(r"除[權息]?交易日(?:為)?[:：]?\s*(\d{4}/\d{2}/\d{2})", note)
    if match:
        return match.group(1)

    # 3. 中文格式（2025年07月25日）
    match = re.search(r"(\d{4})年(\d{2})月(\d{2})日", note)
    if match:
        return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"

    return None

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

