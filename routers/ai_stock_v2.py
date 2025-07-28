from ai_twse_v1 import get_twse_price, get_twse_dividend
from ai_finmind_v1 import get_finmind_price, get_finmind_dividend

async def get_stock_info(stock_id: str, date: str = None) -> dict:
    try:
        data = await get_finmind_price(stock_id, date)
        if not data or "error" in data:
            data = await get_twse_price(stock_id, date)
        return data
    except Exception as e:
        return {"error": str(e)}

async def get_dividend_info(stock_id: str) -> dict:
    try:
        data = await get_finmind_dividend(stock_id)
        if not data or "error" in data:
            data = await get_twse_dividend(stock_id)
        return data
    except Exception as e:
        return {"error": str(e)}
