import os
from fastapi import APIRouter, Header, HTTPException, Request
from linebot import AsyncWebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from utils.verifier import verify_signature

router = APIRouter()
handler = AsyncWebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@router.post("")
async def line_webhook(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    if not verify_signature(body, x_line_signature):
        raise HTTPException(400, "Invalid signature")
    events = await handler.parse_event_request(body, x_line_signature)
    for e in events:
        if isinstance(e, MessageEvent) and isinstance(e.message, TextMessage):
            await handler.reply_message(e.reply_token, TextSendMessage(text="DanielBot 已收到訊息，處理中…"))
    return "ok"
