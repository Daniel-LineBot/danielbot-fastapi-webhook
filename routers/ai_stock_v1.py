# routers/ai_stock_v1.py

from fastapi import APIRouter
from routers.twse import get_price_twse  # 引入 TWSE crawler

from routers.publicinfo import get_price_publicinfo
from routers.goodinfo import get_price_goodinfo

# routers/ai_stock_v1.py ➜ 你的 router_price_autoselector 加上格式化
from routers.formatter import ai_stock_response_formatter

# routers/ai_stock_v1.py ➜ extend router trace
from routers.parser import parse_eps_pe_industry

router = APIRouter()

@router.get("/ai-stock/ping")
async def ping():
    return {"status": "ai_stock_v1 ready"}

@router.get("/ai-stock/price/{stock_id}")
async def price_lookup(stock_id: str):
    result = await get_price_twse(stock_id)
    return result
# routers/ai_stock_v1.py ➜ extend router trace

from routers.parser import parse_eps_pe_industry

@router.get("/ai-stock/price/{stock_id}")
async def router_price_autoselector(stock_id: str):
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

