from fastapi import APIRouter, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import asyncio
import re
from datetime import datetime

from routers.stock import get_stock_info
from routers.dividend import get_dividend_info

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
def handle_text_message(event: MessageEvent):
    asyncio.create_task(process_event(event))


async def process_event(event: MessageEvent):
    user_text = event.message.text.strip()
    reply_text = ""

    # 股票查詢
    if user_text.startswith("查詢"):
        parts = user_text.replace("查詢", "").strip().split()
        stock_id = parts[0] if len(parts) >= 1 else None
        date = parts[1] if len(parts) >= 2 else None

        # 驗證股票代號
        if not stock_id or not re.fullmatch(r"\d{4}", stock_id):
            reply_text = "❗️請輸入正確的四位數股票代號，例如：查詢 2330 或 查詢 2330 20250701"
        elif date:
            if not re.fullmatch(r"\d{8}", date):
                reply_text = "❗️日期格式錯誤，請使用 YYYYMMDD，例如：20250701"
            else:
                try:
                    datetime.strptime(date, "%Y%m%d")
                except ValueError:
                    reply_text = f"❗️查無效日期：{date}"

        if not reply_text:
            try: 
                info = await get_stock_info(stock_id, date)
                print("📦 查股 info 回傳：", info)
            except Exception as e:
                info = {"error": f"查詢時發生例外：{str(e)}"}

            if not isinstance(info, dict):
                reply_text = "⚠️ 查詢回傳資料格式錯誤"
            elif "error" in info:
                reply_text = f"⚠️ {info['error']}"
            elif info.get("資料來源") == "即時查詢":
                reply_text = (
                    f"📈 {info.get('股票名稱', '')}（{info.get('股票代號', '')}）\n"
                    f"成交價：{info.get('成交價', '-')} 元\n"
                    f"開盤：{info.get('開盤', '-')} 元\n"
                    f"產業別：{info.get('產業別', '-')}"
                )
            else:
                reply_text = (
                    f"📊 股票代號：{info.get('股票代號', '')}\n"
                    f"查詢日：{info.get('原始查詢日期', '-')}"
                    f" ➜ 回應日：{info.get('實際回傳日期', '-')}\n"
                    f"開：{info.get('開盤', '-')} 高：{info.get('最高', '-')}"
                    f" 低：{info.get('最低', '-')} 收：{info.get('收盤', '-')}\n"
                    f"成交量：{info.get('成交量(張)', '-')} 張"
                )
                if "提示" in info:
                    reply_text += f"\n🛈 {info['提示']}"

    # 配息查詢
    elif user_text.startswith("查配息"):
        stock_id = user_text.replace("查配息", "").strip()

        if not re.fullmatch(r"\d{4}", stock_id):
            reply_text = "❗️請輸入正確的四位數股票代號，例如：查配息 2330"
        else:
            try:
                info = get_dividend_info(stock_id)
                print("📦 查配息 info 回傳：", info)
            except Exception as e:
                info = {"error": f"查詢配息時發生例外：{str(e)}"}

            if not isinstance(info, dict):
                reply_text = "⚠️ 查詢回傳資料格式錯誤"
            elif "error" in info:
                reply_text = f"⚠️ {info['error']}"
            else:
                reply_text = (
                    f"📅 {info.get('配息年度', '-')} 年 {stock_id} 配息資訊\n"
                    f"除權息日：{info.get('除權息日', '-')} 📆\n"
                    f"現金股利：{info.get('現金股利', '-')} 元\n"
                    f"股票股利：{info.get('股票股利', '-')} 股\n"
                    f"預計發放：{info.get('發放日', '-')} 📮\n"
                    f"來源：{info.get('來源', '-')}\n"
                    f"🛈 {info.get('提示', '-')}"
                )

    else:
        reply_text = (
            f"你剛說的是：{user_text}\n\n"
            "💡 指令範例：\n"
            "➤ 查詢 2330\n"
            "➤ 查詢 2330 20250701\n"
            "➤ 查配息 2330"
        )

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

  
