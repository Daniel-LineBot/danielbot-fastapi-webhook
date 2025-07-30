from fastapi import APIRouter, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from modules.reply_router import reply_router
import os
import asyncio

router = APIRouter()
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@router.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-line-signature")
    handler.handle(body.decode("utf-8"), signature)
    return {"status": "OK"}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    asyncio.create_task(process_event(event))

async def process_event(event: MessageEvent):
    user_text = event.message.text.strip()
    result = await reply_router(user_text)
    reply_text = result.get("text", "查無內容")
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))