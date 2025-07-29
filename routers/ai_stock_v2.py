routers/ai_stock_v2.py
from routers.ai_twse_v1 import get_twse_price, get_twse_dividend
from routers.ai_finmind_v1 import get_finmind_price, get_finmind_dividend
from modules.tdcc_client import get_cdib_dividend
from modules.dividend_reply import get_dividend_info


async def get_stock_info(stock_id: str, date: str = None) -> dict:
    for source, fetcher in [
        ("TWSE", get_twse_price),
        ("FinMind", get_finmind_price)
    ]:
        try:
            data = await fetcher(stock_id, date)
            if data and isinstance(data, dict) and len(data.keys()) > 1:
                data["source"] = source
                return data
        except Exception as e:
            logger.warning(f"[Fallback] {source} 讀取失敗：{e}")
    return {"error": "全部來源都查不到股價資訊", "stock_id": stock_id}


