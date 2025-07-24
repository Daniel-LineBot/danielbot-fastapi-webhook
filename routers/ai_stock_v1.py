# routers/ai_stock_v1.py

from fastapi import APIRouter
from routers.twse import get_price_twse  # 引入 TWSE crawler

from routers.publicinfo import get_price_publicinfo
from routers.goodinfo import get_price_goodinfo


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

