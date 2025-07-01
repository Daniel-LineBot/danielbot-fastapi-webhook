import os
from fastapi import APIRouter, Header, HTTPException, Request
from linebot import AsyncWebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from utils.verifier import verify_signature

router = APIRouter()
handler = AsyncWebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@router.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("x-line-signature", "")
    body = (await request.body()).decode("utf-8")

    print("📩 收到 LINE Webhook 請求")
    print(f"🔐 Signature: {signature}")
    print(f"📦 Body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❗ 無效的簽名")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


async def line_webhook(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    if not verify_signature(body, x_line_signature):
        raise HTTPException(400, "Invalid signature")
    events = await handler.parse_event_request(body, x_line_signature)
    for e in events:
        if isinstance(e, MessageEvent) and isinstance(e.message, TextMessage):
            await handler.reply_message(e.reply_token, TextSendMessage(text="DanielBot 已收到訊息，處理中…"))
    return "ok"
