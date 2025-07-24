from linebot.models import BubbleContainer, BoxComponent, TextComponent, FlexSendMessage
from webhook.log_trace_decorator import log_trace
import logging, json
logger = logging.getLogger("uvicorn")


@log_trace("Bubble UI Builder")
def reply_bubble_builder(response: dict) -> BubbleContainer:
    # ✅ fallback source 檢查器
    ALLOWED_SOURCE = ["TWSE", "Goodinfo", "MOPS"]
    if response.get("source") not in ALLOWED_SOURCE:
        response["source"] += " ⚠️ 非預設來源"

    # ✅ 欄位 validator ➜ 避免 Bubble builder 爆炸
    stock_id = response.get("stock_id") or "未知代碼"
    price = response.get("price") or "--"
    change = response.get("change") or "--"
    #source = response.get("source") or "fallback"
    source = response.get("source", "TWSE")
    if "html" in source.lower():
        source += " 🔍 HTML爬蟲"
    elif "api" in source.lower():
        source += " ⚡ TWSE API"
    elif "fallback" in source.lower():
        source += " ❓ fallback來源"
    elif source not in ["TWSE", "MOPS", "Goodinfo"]:
        source += " ⚠️ 非預設來源"
    timestamp = response.get("timestamp") or "--"

    bubble = BubbleContainer(
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text=f"📈 查詢結果 - {stock_id}", weight="bold", size="md"),
                TextComponent(text=f"成交價：{price} 元", size="sm"),
                TextComponent(text=f"漲跌：{change}", size="sm"),
                TextComponent(text=f"來源：{source}", size="xs", color="#AAAAAA"),
                TextComponent(text=f"資料時間：{timestamp}", size="xs", color="#AAAAAA"),
            ]
        )
    )

    # ✅ Bubble preview logs trace
    logger.info(f"📦 Bubble preview JSON ➜ {json.dumps(bubble.as_json(), ensure_ascii=False)}")
    return bubble


