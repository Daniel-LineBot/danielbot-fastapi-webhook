# ai_stock_v1.py

from routers.twse import get_twse_data
from routers.publicinfo import get_price_publicinfo
from routers.goodinfo import get_price_goodinfo
import asyncio

async def get_stock_info(stock_id: str, date: str = None) -> dict:
    data = await get_stock_data(stock_id, date)
    return {
        "股票代號": stock_id,
        "查詢日期": date,
        "結果": data
    }
    
async def get_stock_data(stock_id: str, date: str = None) -> dict:
    twse_data = await get_twse_data(stock_id, date)
    if twse_data and "收盤" in twse_data:
        return twse_data | {"來源": "TWSE"}

    goodinfo_data = await get_price_goodinfo(stock_id)
    if goodinfo_data and "收盤" in goodinfo_data:
        return goodinfo_data | {"來源": "Goodinfo"}

    public_data = await get_price_publicinfo(stock_id)
    if public_data and "收盤" in public_data:
        return public_data | {"來源": "PublicInfo"}

    return {
        "error": f"【{stock_id}】{date or '今日'} 查無盤後資料，請確認是否為交易日"
    }
"""
async def get_stock_info(stock_id: str, date: str = None) -> dict:
    tasks = [
        get_twse_data(stock_id, date),
        get_price_publicinfo(stock_id),
        get_price_goodinfo(stock_id)
    ]

    twse_data, mops_data, goodinfo_data = await asyncio.gather(*tasks)

    return {
        "股票代號": stock_id,
        "查詢日期": date,
        "TWSE": twse_data or {},
        "MOPS": mops_data or {},
        "Goodinfo": goodinfo_data or {},
        "來源": {
            "TWSE": bool(twse_data),
            "MOPS": bool(mops_data),
            "Goodinfo": bool(goodinfo_data)
        }
    }
    """
