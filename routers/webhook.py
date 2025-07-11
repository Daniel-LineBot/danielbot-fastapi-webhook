from fastapi import APIRouter, Request
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot import LineBotApi, WebhookHandler
from linebot.v3.messaging import AsyncLineBotApi
from linebot.v3.messaging.models import TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError
from linebot.aiohttp_async_http_client import AioHttpAsyncHttpClient
import os
import logging
import re
from datetime import datetime

from routers.stock import get_stock_info  # 已確認為 TWSE 正式版

router = APIRouter()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = AsyncLineBotApi(
    channel_access_token=LINE_CHANNEL_ACCESS_TOKEN,
    http_client=AioHttpAsyncHttpClient()
)
handler = AsyncWebhookHandler(LINE_CHANNEL_SECRET)

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

@router.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-line-signature")

    try:
        await handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        logger.warning("❌ LINE Webhook Signature 驗證失敗")
        return "Invalid signature", 400

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
async def handle_text_message(event: MessageEvent):
    text = event.message.text.strip()
    reply_text = ""

    if text.startswith("查詢"):
        args = text.replace("查詢", "").strip().split()
        stock_id = args[0] if len(args) >= 1 else ""
        date = args[1] if len(args) >= 2 else None

        if not re.fullmatch(r"\d{4}", stock_id):
            reply_text = "❗️請輸入正確的四位數股票代號，例如：查詢 2330"
        elif date and not re.fullmatch(r"\d{8}", date):
            reply_text = "❗️日期格式錯誤，請使用 YYYYMMDD，例如：20250701"
        else:
            try:
                if date:
                    datetime.strptime(date, "%Y%m%d")
                    info = await get_stock_info(stock_id, date)
                else:
                    info = await get_stock_info(stock_id)

                logger.info(f"📦 查股 info 回傳：{info}")
            except Exception as e:
                reply_text = f"⚠️ 查詢時發生錯誤：{str(e)}"
                logger.exception(f"📛 查股例外：{str(e)}")
                info = {}

            if isinstance(info, dict) and "error" in info:
                reply_text = f"⚠️ {info['error']}"
            elif info.get("成交價") or info.get("收盤"):
                reply_text = (
                    f"📈 {info.get('股票名稱', '')}（{info.get('股票代號', '')}）\n"
                    f"成交價：{info.get('成交價', info.get('收盤', '-'))} 元\n"
                    f"開盤：{info.get('開盤', '-')} 元\n"
                    f"產業別：{info.get('產業別', info.get('資料來源', '-'))}"
                )

                if info.get("提示"):
                    reply_text += f"\n💡 {info['提示']}"
            else:
                reply_text = "⚠️ 查無資料，請確認股票代號或日期是否正確"
    else:
        reply_text = (
            f"你剛說的是：{text}\n\n"
            "💡 指令範例：\n查詢 2330\n查詢 2330 20250701"
        )

    try:
        await line_bot_api.reply_message(
            event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
    except Exception as e:
        logger.exception(f"📛 回覆訊息失敗：{str(e)}")
