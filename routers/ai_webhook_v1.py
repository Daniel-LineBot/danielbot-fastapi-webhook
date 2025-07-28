from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os, logging, re
from asyncio import create_task
from ai_stock_v2 import get_stock_info, get_dividend_info

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
    text = event.message.text.strip()
    reply_token = event.reply_token
    reply_text = ""

    match = re.match(r"(查詢|股價|配息)\s*(\d{4})(?:\s*(\d{8}))?", text)
    if match:
        cmd, stock_id, date = match.groups()
        try:
            if cmd == "配息":
                info = await get_dividend_info(stock_id)
                reply_text = (
                    f"💰 {stock_id} 配息資訊\n"
                    f"年度：{info.get('year', '-')}\n"
                    f"現金股利：{info.get('cash_dividend', '-')}\n"
                    f"股票股利：{info.get('stock_dividend', '-')}\n"
                    f"除權息日：{info.get('ex_dividend_date', '-')}\n"
                    f"來源：{info.get('source', '-')}"
                )
            else:
                info = await get_stock_info(stock_id, date)
                reply_text = (
                    f"📈 {info.get('name', '')}（{stock_id}）\n"
                    f"成交價：{info.get('price', '-')}\n"
                    f"開盤：{info.get('open', '-')}\n"
                    f"最高：{info.get('high', '-')}\n"
                    f"最低：{info.get('low', '-')}\n"
                    f"成交量：{info.get('volume', '-')}\n"
                    f"查詢日期：{info.get('date', '-')}\n"
                    f"來源：{info.get('source', '-')}"
                )
        except Exception as e:
            logger.exception(f"📛 查詢失敗：{e}")
            reply_text = f"⚠️ 查詢失敗：{str(e)}"
    else:
        reply_text = (
            f"你剛說的是：{text}\n\n"
            "💡 指令範例：\n查詢 2330\n查詢 2330 20250701\n配息 2330"
        )

    try:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_text))
    except Exception as e:
        logger.exception(f"📛 回覆訊息失敗：{e}")
