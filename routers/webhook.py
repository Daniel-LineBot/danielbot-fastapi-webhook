from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os
import logging
import re
from datetime import datetime
from asyncio import create_task

from routers.ai_stock_v1 import get_stock_info  # ✅ 改用整合模組 

from utils.fallback_chain import query_stock_with_fallbacks
import re

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

    # 假設你已從 event 中抽出 stock_id（例如 "查詢 2330"）
    stock_id = extract_stock_id_from_event(...)  # 自行定義解析方式
    data = await query_stock_with_fallbacks(stock_id)

    # callback reply（根據查詢結果）
    if "error" in data:
        reply_text = f"⚠️ 查詢失敗 ➜ {data['error']}"
    else:
        reply_text = (
            f"📈 {stock_id} 查詢成功\n"
            f"收盤：{data['收盤']}\n"
            f"成交量：{data['成交量']}\n"
            f"來源：{data['查詢來源']}\n"
            f"查詢日期：{data['查詢日期']}"
        )

    # LINE 回覆處理邏輯...

@handler.add(MessageEvent)
def handle_message(event):
    create_task(process_event(event))

async def process_event(event):
    if isinstance(event.message, TextMessage):
        await handle_text_message(event)

async def handle_text_message(event):
    stock_id = extract_stock_id(event.message.text)
    data = await query_stock_with_fallbacks(stock_id)

    if "error" in data:
        reply_text = f"查詢失敗：{data['error']}"
    else:
        reply_text = (
            f"📈 {stock_id} 查詢結果\n"
            f"收盤：{data['收盤']}\n"
            f"成交量：{data['成交量']}\n"
            f"來源：{data['查詢來源']}\n"
            f"查詢日期：{data['查詢日期']}"
        )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


def extract_stock_id_from_event(text: str) -> str:
    """
    從 LINE 訊息中解析出股票代號，例如「查詢 2330」、「股價 2603」
    """
    # 清理空格 & 去掉「查詢」、「股價」等前綴
    cleaned = re.sub(r"(查詢|查|股價|看看)", "", text, flags=re.IGNORECASE).strip()

    # 只留下 4 位數股票代號
    match = re.fullmatch(r"\d{4}", cleaned)
    return match.group(0) if match else ""


async def process_event(event: MessageEvent):
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
                industry = info.get("產業別") or info.get("資料來源", "-")
                
                reply_text = (
                    f"📈 {info.get('股票名稱', '')}（{info.get('股票代號', '')}）\n"
                    f"成交價：{info.get('成交價', info.get('收盤', '-'))} 元\n"
                    f"開盤：{info.get('開盤', '-')} 元\n"
                    f"產業別：{industry}"
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
        logger.info(f"✅ 準備回覆 LINE ➜ token={event.reply_token}, text={reply_text}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        logger.info(f"✅ 準備回覆 LINE ➜ token={event.reply_token}, text={reply_text}")
    except Exception as e:
        logger.exception(f"📛 回覆訊息失敗：{str(e)}")


"""

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent):
    try:
        logger.info(f"✅ webhook 收到 LINE 訊息：{event.message.text}")
        create_task(process_event(event))
    except Exception as e:
        logger.exception(f"📛 webhook callback 發生例外：{str(e)}")
"""
