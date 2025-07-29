# utils/stock_parser.py

import re

# 簡易對照表（可擴充成完整 mapping）
NAME_TO_ID = {
    "台積電": "2330",
    "聯電": "2303",
    "鴻海": "2317",
}

KEYWORDS = {
    "price": ["股價", "行情", "目前價格"],
    "dividend": ["配息", "股利", "殖利率"],
    "profile": ["基本資料", "產業", "市值"]
}

def extract_stock_id(text: str) -> str | None:
    match = re.search(r"\d{4}", text)
    if match:
        return match.group()
    for name, stock_id in NAME_TO_ID.items():
        if name in text:
            return stock_id
    return None

def normalize_query_type(text: str) -> str | None:
    for qtype, keywords in KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return qtype
    return None
