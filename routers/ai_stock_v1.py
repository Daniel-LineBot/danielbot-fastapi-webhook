# ai_stock_v1.py

from routers.twse import get_twse_data
from routers.publicinfo import get_mops_metadata
from routers.goodinfo import get_goodinfo_metadata
import asyncio

async def get_stock_info(stock_id: str, date: str = None) -> dict:
    tasks = [
        get_twse_data(stock_id, date),
        get_mops_metadata(stock_id),
        get_goodinfo_metadata(stock_id)
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
