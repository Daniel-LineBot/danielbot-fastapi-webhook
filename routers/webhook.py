from fastapi import APIRouter, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

from routers.stock import get_stock_info  # 匯入你的查詢模組

router = APIRouter()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@router.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-line-signature")

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_text = event.message.text.strip()

    if user_text.startswith("查詢"):
        parts = user_text.replace("查詢", "").strip().split()
        stock_id = parts[0] if len(parts) >= 1 else None
        date = parts[1] if len(parts) >= 2 else None

        if not stock_id:
            reply_text = "請輸入股票代號，例如：查詢 2330 或 查詢 2330 20250628"
        else:
            import asyncio
            info = asyncio.run(get_stock_info(stock_id, date))

            if "error" in info:
                reply_text = f"⚠️ {info['error']}"
            elif info["資料來源"] == "即時查詢":
                reply_text = (
                    f"📈 {info['股票名稱']}（{info['股票代號']}）\n"
                    f"成交價：{info['成交價']} 元\n"
                    f"開盤：{info['開盤']} 元\n"
                    f"產業別：{info['產業別']}"
                )
            else:
                reply_text = (
                    f"📊 股票代號：{info['股票代號']}\n"
                    f"查詢日：{info['原始查詢日期']} ➜ 回應日：{info['實際回傳日期']}\n"
                    f"開：{info['開盤']} 高：{info['最高']} 低：{info['最低']} 收：{info['收盤']}\n"
                    f"成交量：{info['成交量(張)']} 張"
                )
                if "提示" in info:
                    reply_text += f"\n🛈 {info['提示']}"
    else:
        reply_text = f"你剛說的是：{user_text}（若要查股價請輸入「查詢 2330」）"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


