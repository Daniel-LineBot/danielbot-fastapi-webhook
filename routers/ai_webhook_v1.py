from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os, logging, re
from asyncio import create_task
from routers.ai_stock_v2 import get_stock_info, get_dividend_info
from utils.query_metadata_parser import get_query_metadata
from modules.reply_router import reply_router


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
        return PlainTextResponse("Invalid signature", status_code=400)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    create_task(process_event(event))

async def process_event(event: MessageEvent):
    user_text = event.message.text.strip()
    reply_token = event.reply_token

    metadata = get_query_metadata(user_text)
    reply_text = await reply_router(metadata)

    try:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_text))
    except Exception as e:
        logger.exception(f"📛 回覆訊息失敗：{e}")
