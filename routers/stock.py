from fastapi import APIRouter, Request, Query
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os
import logging
import re
import asyncio
from datetime import datetime, timedelta, time
from typing import Optional, Union
import httpx

router = APIRouter()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

def is_twse_open():
    now = datetime.now().time()
    return time(9, 0) <= now <= time(13, 30)

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
def handle_text_message(event: MessageEvent):
    text = event.message.text.strip()
    reply_text = ""

    try:
        info = asyncio.run(get_response_info(text))
        if isinstance(info, str):
            reply_text = info
        elif info.get("error"):
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
    except Exception as e:
        logger.exception(f"📛 查股例外：{str(e)}")
        reply_text = f"⚠️ 查詢時發生錯誤：{str(e)}"

    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    except Exception as e:
        logger.exception(f"📛 回覆訊息失敗：{str(e)}")

async def get_response_info(text: str):
    if text.startswith("查詢"):
        args = text.replace("查詢", "").strip().split()
        stock_id = args[0] if len(args) >= 1 else ""
        date = args[1] if len(args) >= 2 else None

        if not re.fullmatch(r"\d{4}", stock_id):
            return "❗️請輸入正確的四位數股票代號，例如：查詢 2330"
        elif date and not re.fullmatch(r"\d{8}", date):
            return "❗️日期格式錯誤，請使用 YYYYMMDD，例如：20250701"
        else:
            if date:
                datetime.strptime(date, "%Y%m%d")
                return await get_stock_info(stock_id, date)
            else:
                return await get_stock_info(stock_id)
    else:
        return (
            f"你剛說的是：{text}\n\n"
            "💡 指令範例：\n查詢 2330\n查詢 2330 20250701"
        )

async def get_stock_info(stock_id: str, date: Optional[Union[str, None]] = None):
    logger.info("🪛 DanielBot stock.py ➜ 已啟動 get_stock_info handler")
    logger.info(f"📦 傳入 stock_id={stock_id}, date={repr(date)}")

    if date and not isinstance(date, str):
        date = str(date)

    if date and date.strip():
        logger.info(f"🧮 使用者指定日期 ➜ {date.strip()} ➜ 啟用 get_historical_data()")
        return await get_historical_data(stock_id, date.strip())

    logger.info("🧭 未提供有效 date ➜ 啟用 fallback 判斷")
    now_time = datetime.now().strftime("%H:%M:%S")
    mode = "即時查詢" if is_twse_open() else "歷史查詢"
    logger.info(f"🧪 fallback 判斷 ➜ 現在時間：{now_time} ➜ 模式：{mode}")

    if is_twse_open():
        return await get_realtime_data(stock_id)
    else:
        today = datetime.today().strftime("%Y%m%d")
        logger.info(f"[TWSE fallback] 市場已收盤 ➜ fallback 查詢今日盤後 ➜ {today}")
        return await get_historical_data(stock_id, today)

async def get_realtime_data(stock_id: str):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.twse.com.tw/"
    }

    logger.info(f"📡 [TWSE 即時] 發送查詢 ➜ stock_id={stock_id}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10, follow_redirects=True)
            logger.info(f"[TWSE 即時] 回應狀態 ➜ {response.status_code}")
            try:
                data = response.json()
                logger.info(f"[TWSE 即時] 回傳 JSON：{data}")
            except Exception as je:
                logger.exception(f"[TWSE 即時] 回傳無法解析 JSON ➜ {str(je)}")
                return {"error": "TWSE 回傳格式錯誤，請稍後再試"}
        except Exception as e:
            logger.exception(f"[TWSE 即時] 查詢失敗 ➜ {str(e)}")
            return {"error": "TWSE 即時查詢錯誤，請稍後重試"}

    if not data.get("msgArray"):
        logger.warning(f"[TWSE 即時] 查無代號 ➜ {stock_id}，回傳內容：{data}")
        return {"error": "找不到股票代號，請確認輸入是否正確"}

    info = data["msgArray"][0]
    logger.info(f"[TWSE 即時] 成交價 ➜ {info.get('z')} ➜ 查詢成功")
    return {
        "資料來源": "即時查詢",
        "股票名稱": info.get("n", ""),
        "股票代號": info.get("c", ""),
        "成交價": info.get("z", ""),
        "漲跌": info.get("y", ""),
        "昨收": info.get("y", ""),
        "開盤": info.get("o", ""),
        "產業別": info.get("ind", "N/A")
    }

async def get_historical_data(stock_id: str, date: str):
    logger.info(f"📦 [TWSE 歷史] 進入歷史查詢 ➜ stock_id={stock_id}, date={date}")
    try:
        original_query_date = datetime.strptime(str(date), "%Y%m%d")
    except ValueError:
        logger.warning(f"[TWSE 歷史] 日期格式錯誤 ➜ {date}")
        return {"error": "請使用 YYYYMMDD 格式輸入日期（例如 20250701）"}

    target_date = original_query_date
    retries = 7
    fallback_used = False

    for _ in range(retries):
        query_month = target_date.strftime("%Y%m")
        query_day = f"{target_date.year}/{target_date.month}/{target_date.day}"
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={query_month}01&stockNo={stock_id}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.twse
