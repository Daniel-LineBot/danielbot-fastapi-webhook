import re
from loguru import logger

from routers.twse import get_twse_name
from routers.twse import get_twse_industry
from routers.twse import fetch_twse_metadata

#from routers.goodinfo import get_goodinfo_name
#from routers.goodinfo import get_goodinfo_industry

#from routers.stock import get_stock_info

async def get_stock_name_industry(stock_id: str) -> dict:
    """
    從 TWSE OpenAPI 取得股票名稱與產業別 ➜ 用於 callback reply 補上 metadata
    """
    stock_id = str(stock_id).strip()
    if not re.fullmatch(r"\d{4}", stock_id):
        return {"股票代號": stock_id, "股票名稱": "格式錯誤", "產業別": "查無"}

    try:
        metadata = await fetch_twse_metadata()
        info = metadata.get(stock_id, {})
        name = info.get("name", "查無")
        category = info.get("category", "N/A")
        logger.info(f"🔍 TWSE metadata ➜ {stock_id} ➜ {name} ➜ {category}")
        return {
            "股票代號": stock_id,
            "股票名稱": name,
            "產業別": category
        }
    except Exception as e:
        logger.exception(f"❌ TWSE metadata 取得失敗 ➜ {str(e)}")
        return {
            "股票代號": stock_id,
            "股票名稱": "查無",
            "產業別": "查無"
        }

