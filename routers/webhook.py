from fastapi import APIRouter, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import logging
import re
import asyncio

from routers.stock import get_stock_info

router = APIRouter()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


@router.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-line-signature")

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        logger.warning("❌ LINE Webhook Signature 驗證失敗")
        return "Invalid signature", 400

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent):  # ✅ 使用同步 callback
    try:
        logger.info(f"✅ webhook 收到 LINE 訊息：{event.message.text}")
        asyncio.create_task(process_event(event))  # ✅ coroutine 觸發成功
    except Exception as e:
        logger.exception(f"📛 webhook callback 發生例外：{str(e)}")


async def process_event(event: MessageEvent):
    text = event.message.text.strip()
    reply_text = ""

    if text.startswith("查詢"):
        stock_id = text.replace("查詢", "").strip()
        if not re.fullmatch(r"\d{4}", stock_id):
            reply_text = "❗️請輸入正確的四位數股票代號，例如：查詢 2330"
        else:
            try:
                info = await get_stock_info(stock_id)
                logger.info(f"📦 查股 info 回傳：{info}")
            except Exception as e:
                reply_text = f"⚠️ 查詢時發生錯誤：{str(e)}"
                logger.exception("📛 查股例外")
                info = {}

            if isinstance(info, dict) and "error" in info:
                reply_text = f"⚠️ {info['error']}"
            elif info.get("成交價"):
                reply_text = (
                    f"📈 {info.get('股票名稱', '')}（{info.get('股票代號', '')}）\n"
                    f"成交價：{info.get('成交價', '-')} 元\n"
                    f"開盤：{info.get('開盤', '-')} 元\n"
                    f"產業別：{info.get('產業別', '-')}"
                )
            else:
                reply_text = "⚠️ 查無資料，請確認股票代號是否正確"

    else:
        reply_text = (
            f"你剛說的是：{text}\n\n"
            "💡 指令範例：查詢 2330"
        )

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
