# routers/twse.py
import re
from loguru import logger
import httpx

TWSE_URL = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"

async def fetch_twse_metadata() -> dict:
    """
    從 TWSE OpenAPI 取得所有上市公司基本資料 ➜ 回 dict: {stock_id: {name, industry}}
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(TWSE_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"📦 TWSE metadata loaded ➜ 共 {len(data)} 筆")
            return {
                item["公司代號"]: {
                    "name": item["公司簡稱"],
                    "industry": item["產業別"]
                }
                for item in data if item.get("公司代號") and item.get("公司簡稱")
            }
    except Exception as e:
        logger.exception(f"❌ TWSE metadata fetch failed ➜ {str(e)}")
        return {}

async def get_twse_name(stock_id: str) -> str:
    metadata = await fetch_twse_metadata()
    return metadata.get(stock_id, {}).get("name", "查無")

async def get_twse_industry(stock_id: str) -> str:
    metadata = await fetch_twse_metadata()
    return metadata.get(stock_id, {}).get("industry", "未分類")

def twse_is_valid_id(stock_id: str) -> bool:
    return bool(re.fullmatch(r"\d{4}", stock_id)) and stock_id in twse_stock_table
