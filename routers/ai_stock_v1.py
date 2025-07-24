# routers/ai_stock_v1.py

from fastapi import APIRouter
from routers.twse import get_price_twse  # 引入 TWSE crawler

from routers.publicinfo import get_price_publicinfo
from routers.goodinfo import get_price_goodinfo

# routers/ai_stock_v1.py ➜ 你的 router_price_autoselector 加上格式化
from routers.formatter import ai_stock_response_formatter

# routers/ai_stock_v1.py ➜ extend router trace
from routers.parser import parse_eps_pe_industry

from routers.parser import parse_eps_pe_industry

from routers.twse_selector import twse_router_selector
import logging
logger = logging.getLogger("uvicorn")

router = APIRouter()

@router.get("/ai-stock/ping")
async def ping():
    return {"status": "ai_stock_v1 ready"}
"""
@router.get("/ai-stock/price/{stock_id}")
async def price_lookup(stock_id: str):
    metadata = await twse_router_selector(stock_id)
    logger.info(f"✅ TWSE查價完成 ➜ metadata: {metadata}")
    return metadata
"""
@router.get("/ai-stock/price/{stock_id}")
async def price_lookup(stock_id: str):
    metadata = await router_price_autoselector(stock_id)
    logger.info(f"✅ LINBot查價完成 ➜ metadata: {metadata}")
    return metadata



# routers/ai_stock_v1.py ➜ extend router trace


@router.get("/ai-stock/price/{stock_id}")
async def router_price_autoselector(stock_id: str):
 # 🟡 Step 1 ➜ 嘗試從 Firestore 快取讀資料
    cached = await db.collection("ai_stock_metadata").document(stock_id).get()
    if cached.exists:
        cached_data = cached.to_dict()
        cached_data["fallback階層"] = "Firestore Cache"
        return ai_stock_response_formatter_enhanced(cached_data)    
    for fn, level in [
        (get_price_twse, "TWSE"),
        (get_price_publicinfo, "公開資訊觀測站"),
        (get_price_goodinfo, "Goodinfo")
    ]:
        raw = await fn(stock_id)
        if raw and "收盤" in raw:
            raw["fallback階層"] = level

            # Step 2.10 ➜ crawler metadata抽取後 merge到 raw
            if "原始HTML" in raw:
                metadata = parse_eps_pe_industry(raw["原始HTML"])
                raw.update(metadata)

            # logs trace ➜ 畫 fallback流向
            router_trace_visualizer(
                stock_id=stock_id,
                source=raw.get("來源", "未知"),
                level=level,
                metadata=raw
            )

            return ai_stock_response_formatter_enhanced(raw)

    # fallback全炸 ➜ formatter錯誤包裝
    return ai_stock_response_formatter_enhanced({
        "error": f"{stock_id} 查價失敗 ➜ 全部來源炸掉",
        "fallback階層": "無回應"
    })



