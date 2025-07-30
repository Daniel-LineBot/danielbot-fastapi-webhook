#routers/ai_stock_v2.py
from routers.ai_twse_v1 import get_twse_price, get_twse_dividend
from routers.ai_finmind_v1 import get_finmind_price, get_finmind_dividend
from modules.tdcc_client import get_cdib_dividend
from modules.dividend_reply import get_dividend_info
from loguru import logger  # ✅ 必要補上這行


from loguru import logger
from routers.ai_twse_v1 import get_twse_price
from routers.ai_finmind_v1 import get_finmind_price

async def get_stock_info(stock_id: str, date: str = None) -> dict:
    source_chain = []

    async def try_fetch(fetcher, label: str):
        try:
            data = await fetcher(stock_id, date)
            if data and isinstance(data, dict) and len(data.keys()) > 1 and not data.get("error"):
                source_chain.append(f"{label} ✔︎")
                return {"source_chain": source_chain, "final_result": data}
            else:
                source_chain.append(f"{label} ✖︎")
        except Exception as e:
            logger.warning(f"[Fallback] {label} 查詢錯誤：{e}")
            source_chain.append(f"{label} ✖︎")
        return None

    for fetcher, label in [
        (get_twse_price, "TWSE"),
        (get_finmind_price, "FinMind")
    ]:
        result = await try_fetch(fetcher, label)
        if result:
            return result

    # 全部來源都沒命中
    return {
        "source_chain": source_chain,
        "final_result": {
            "error": f"{stock_id} 查無股價資訊",
            "stock_id": stock_id
        }
    }



