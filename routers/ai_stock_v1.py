# routers/ai_stock_v1.py

from fastapi import APIRouter
from routers.twse import get_price_twse  # 引入 TWSE crawler

from routers.publicinfo import get_price_publicinfo
from routers.goodinfo import get_price_goodinfo

# routers/ai_stock_v1.py ➜ 你的 router_price_autoselector 加上格式化
from routers.formatter import ai_stock_response_formatter


router = APIRouter()

@router.get("/ai-stock/ping")
async def ping():
    return {"status": "ai_stock_v1 ready"}

@router.get("/ai-stock/price/{stock_id}")
async def price_lookup(stock_id: str):
    result = await get_price_twse(stock_id)
    return result
@router.get("/ai-stock/price/{stock_id}")
async def router_price_autoselector(stock_id: str):
    # Step 1 ➜ 試 TWSE crawler
    twse = await get_price_twse(stock_id)
    if twse and "收盤" in twse:
        twse["fallback階層"] = "TWSE"
        return twse

    # Step 2 ➜ fallback 公開資訊觀測站
    publicinfo = await get_price_publicinfo(stock_id)
    if publicinfo and "收盤" in publicinfo:
        publicinfo["fallback階層"] = "公開資訊觀測站"
        return publicinfo

    # Step 3 ➜ fallback Goodinfo
    goodinfo = await get_price_goodinfo(stock_id)
    if goodinfo and "收盤" in goodinfo:
        goodinfo["fallback階層"] = "Goodinfo"
        return goodinfo

    # fallback 全炸 ➜ 回錯誤 trace
    return {
        "error": f"{stock_id} 查價失敗 ➜ TWSE ➔ 公開資訊 ➔ Goodinfo 全部炸掉",
        "fallback階層": "無回應",
        "提示": "請稍後再試或確認代碼是否正確"
    }

@router.get("/ai-stock/price/{stock_id}")
async def router_price_autoselector(stock_id: str):
    for fn, level in [
        (get_price_twse, "TWSE"),
        (get_price_publicinfo, "公開資訊觀測站"),
        (get_price_goodinfo, "Goodinfo")
    ]:
        result = await fn(stock_id)
        if result and "收盤" in result:
            result["fallback階層"] = level
            return ai_stock_response_formatter(result)

    return ai_stock_response_formatter({
        "error": f"{stock_id} 查價失敗 ➜ 全部來源炸掉",
        "fallback階層": "無回應"
    })

