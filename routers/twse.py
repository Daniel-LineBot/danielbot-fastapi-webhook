# routers/twse.py
import re
from loguru import logger

# 🔍 模擬 TWSE 股票對照表 ➜ 可換成爬蟲結果或本地 cache
twse_stock_table = {
    "2330": "台積電",
    "2317": "鴻海",
    "2303": "聯電",
    "5880": "合庫金",
    "2412": "中華電",
}

twse_industry_table = {
    "2330": "半導體",
    "2317": "電子代工",
    "2303": "晶圓製造",
    "5880": "金融控股",
    "2412": "電信服務",
}

def get_twse_name(stock_id: str) -> str:
    stock_id = str(stock_id).strip()
    name = twse_stock_table.get(stock_id, "查無")
    logger.info(f"📌 get_twse_name ➜ {stock_id} ➜ {name}")
    return name

def get_twse_industry(stock_id: str) -> str:
    stock_id = str(stock_id).strip()
    industry = twse_industry_table.get(stock_id, "未分類")
    logger.info(f"🏷️ get_twse_industry ➜ {stock_id} ➜ {industry}")
    return industry

def twse_is_valid_id(stock_id: str) -> bool:
    return bool(re.fullmatch(r"\d{4}", stock_id)) and stock_id in twse_stock_table
