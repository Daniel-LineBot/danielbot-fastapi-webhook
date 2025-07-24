# routers/twse_selector.py
import logging
from routers.twse import get_price_twse_html  # 你原來的版本
from routers.twse_api import get_price_twse_json  # 建議另建 twse_api.py 放 JSON crawler
from webhook.env_config import use_json_metadata
logger = logging.getLogger("uvicorn")

async def twse_router_selector(stock_id: str, use_json: bool = True) -> dict:
    if use_json:
        logger.info(f"🔄 TWSE crawler selector ➜ 使用 JSON metadata API")
        return await get_price_twse_json(stock_id)
    else:
        logger.info(f"🔄 TWSE crawler selector ➜ 使用 HTML月成交爬蟲")
        return await get_price_twse_html(stock_id)
