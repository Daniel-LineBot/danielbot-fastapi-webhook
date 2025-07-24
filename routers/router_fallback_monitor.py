# routers/router_fallback_monitor.py
import logging
logger = logging.getLogger("uvicorn")

def fallback_trace_monitor(stock_id: str, metadata: dict):
    required_fields = ["price", "change", "timestamp", "名稱"]
    missing = [field for field in required_fields if not metadata.get(field)]
    if missing:
        logger.warning(f"⛔ Bubble可能炸 ➜ stock_id: {stock_id} ➜ 缺欄位: {missing}")
    else:
        logger.info(f"✅ metadata欄位完整 ➜ stock_id: {stock_id}")
