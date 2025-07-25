import httpx
from routers.twse import get_twse_data
from routers.goodinfo import get_goodinfo_data
from routers.mops import get_mops_data

async def query_stock_with_fallbacks(stock_id: str) -> dict:
    log_chain = []

    twse_result = await get_twse_data(stock_id)
    if "error" not in twse_result and twse_result.get("收盤"):
        twse_result["查詢來源"] = "TWSE"
        twse_result["查詢日期"] = twse_result.get("資料時間")
        twse_result["fallback_chain"] = log_chain
        return twse_result
    log_chain.append("TWSE failed")

    goodinfo_result = await get_goodinfo_data(stock_id)
    if "error" not in goodinfo_result and goodinfo_result.get("收盤"):
        goodinfo_result["查詢來源"] = "Goodinfo"
        goodinfo_result["查詢日期"] = goodinfo_result.get("資料時間")
        goodinfo_result["fallback_chain"] = log_chain
        return goodinfo_result
    log_chain.append("Goodinfo failed")

    mops_result = await get_mops_data(stock_id)
    if "error" not in mops_result:
        mops_result["查詢來源"] = "MOPS"
        mops_result["查詢日期"] = mops_result.get("資料時間")
        mops_result["fallback_chain"] = log_chain
        return mops_result
    log_chain.append("MOPS failed")

    return {
        "error": "所有來源皆查無資料",
        "fallback_chain": log_chain
    }
