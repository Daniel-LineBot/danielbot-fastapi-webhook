from fastapi import APIRouter, Request, Header, HTTPException
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApiClient, TextMessage
from linebot.v3.webhooks import MessageEvent
from linebot.v3.exceptions import InvalidSignatureError
import asyncio

from app.dependencies import get_line_handler, get_line_client
from app.utils import get_stock_info  # 這必須是 async def

router = APIRouter()

# 初始化 LINE SDK handler/client
handler: WebhookHandler = get_line_handler()
client: MessagingApiClient = get_line_client()

# webhook entrypoint
@router.post("/webhook")
async def webhook(request: Request, x_line_signature: str = Header(...)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

# SYNC wrapper handler ➜ 建立 async background task
@handler.add(MessageEvent, message=TextMessage)
def handle_text_event(event: MessageEvent):
    asyncio.create_task(process_text_message(event))

# 真正處理邏輯的 async 函式
async def process_text_message(event: MessageEvent):
    user_input = event.message.text.strip()
    if user_input.startswith("查股價"):
        stock_id = user_input[3:].strip()  # 例如「查股價2330」
        try:
            result = await get_stock_info(stock_id)
            message = TextMessage(text=f"{stock_id} 現價：{result['price']} 元")
        except Exception as e:
            message = TextMessage(text=f"查詢失敗：{str(e)}")
        await client.reply_message(reply_token=event.reply_token, messages=[message])
