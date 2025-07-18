from fastapi import APIRouter, Request
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
import requests
from bs4 import BeautifulSoup
#20250718_v1

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
        logger.warning("??LINE Webhook Signature 驗�?失�?")
        return "Invalid signature", 400
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent):
    text_raw = event.message.text.strip()
    text = text_raw.replace(" ", "")
    logger.info(f"[Webhook Text] ?��? ??{repr(text_raw)} ??清�?�???{repr(text)}")

    # ???�息模�??��??�斷
    if re.match(r"^?�息\d{4}$", text):
        stock_id = re.sub(r"[^\d]", "", text)
        result = get_dividend_info(stock_id)
        if result.get("error"):
            reply_text = f"?��? {result['error']}"
        else:
            reply_text = (
                f"?�� {result['?�票�??']} ?�息資�?\n"
                f"年度：{result['?�息年度']}\n"
                f"?��??�日：{result['?��??�日']}\n"
                f"?��??�利：{result['?��??�利']} ?�\n"
                f"?�票?�利：{result['?�票?�利']} ?�\n"
                f"?�放?��?{result['?�放??]}\n"
                f"來�?：{result['?��?來�?']}（{result['來�?']}）\n"
                f"?�� {result['?�示']}"
            )
        try:
            logger.info(f"[LINE?��?] ??{repr(reply_text)}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        except Exception as e:
            logger.exception(f"?? ?��??�息訊息失�?：{str(e)}")
        return  # ?��? 記�? return，避?�進入?�股 fallback

    # ?? ?�股模�? ???��??��??�查詢�?輯接?��??�即??    text = text_raw  # 你�??��??�股模�?就�??��??��? text_raw
    reply_text = ""
    try:
        info = asyncio.run(get_response_info(text))
        if isinstance(info, str):
            reply_text = info
        elif info.get("error"):
            reply_text = f"?��? {info['error']}"
        elif info.get("?�交??) or info.get("?�盤"):
            reply_text = (
                f"?? {info.get('?�票?�稱', '')}（{info.get('?�票�??', '')}）\n"
                f"?�交?��?{info.get('?�交??, info.get('?�盤', '-') )} ?�\n"
                f"?�盤：{info.get('?�盤', '-') } ?�\n"
                f"?�業?��?{info.get('?�業??, info.get('資�?來�?', '-') )}"
            )
            if info.get("?�示"):
                reply_text += f"\n?�� {info['?�示']}"
        else:
            reply_text = "?��? ?�無資�?，�?確�??�票�???�日?�是?�正�?
    except Exception as e:
        logger.exception(f"?? ?�股例�?：{str(e)}")
        reply_text = f"?��? ?�詢?�發?�錯誤�?{str(e)}"

    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    except Exception as e:
        logger.exception(f"?? ?��?訊息失�?：{str(e)}")
async def get_response_info(text: str):
    if text.startswith("?�詢"):
        args = text.replace("?�詢", "").strip().split()
        stock_id = args[0] if len(args) >= 1 else ""
        date = args[1] if len(args) >= 2 else None

        if not re.fullmatch(r"\d{4}", stock_id):
            return "?��?請輸?�正確�??��??�股票代?��?例�?：查�?2330"
        elif date and not re.fullmatch(r"\d{8}", date):
            return "?��??��??��??�誤，�?使用 YYYYMMDD，�?如�?20250715"
        else:
            if date:
                datetime.strptime(date, "%Y%m%d")
                return await get_stock_info(stock_id, date)
            else:
                return await get_stock_info(stock_id)
    else:
        return (
            f"你�?說�??��?{text}\n\n"
            "?�� ?�令範�?：\n?�詢 2330\n?�詢 2330 20250715"
        )
def get_goodinfo_data(stock_id: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://goodinfo.tw"
        }
        url = f"https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID={stock_id}"
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # ?�票?�稱�??
        title = soup.title.string.strip()
        stock_name = title.split("(")[0].strip() if "(" in title else "?�知"

        # ?�交?�解??        price_tag = soup.select_one("#divPriceDetail .bg_h1")
        price = price_tag.text.strip() if price_tag else "?�無"

        logger.info(f"[Goodinfo Fallback] ?�票={stock_id} ???�交??{price}")
        return {
            "資�?來�?": "Goodinfo fallback",
            "?�票�??": stock_id,
            "?�票?�稱": stock_name,
            "?�交??: price,
            "?�盤": "-",
            "?�業??: "N/A",
            "?�示": "?�� TWSE 資�??�常 ???�傳 Goodinfo ?�詢結�?"
        }
    except Exception as e:
        logger.exception(f"[Goodinfo Fallback] ?�詢失�? ??{str(e)}")
        return {"error": f"Goodinfo fallback ?�詢失�?：{str(e)}"}        
async def get_stock_info(stock_id: str, date: Optional[Union[str, None]] = None):
    logger.info("?? DanielBot stock.py ??已�???get_stock_info handler")
    logger.info(f"?�� ?�入 stock_id={stock_id}, date={repr(date)}")

    if date and not isinstance(date, str):
        date = str(date)

    if date and date.strip():
        logger.info(f"?�� 使用?��?定日????{date.strip()} ???�用 get_historical_data()")
        return await get_historical_data(stock_id, date.strip())

    logger.info("?�� ?��?供�???date ???�用 fallback ?�斷")
    now_time = datetime.now().strftime("%H:%M:%S")
    mode = "?��??�詢" if is_twse_open() else "歷史?�詢"
    logger.info(f"?�� fallback ?�斷 ???�在?��?：{now_time} ??模�?：{mode}")

    if is_twse_open():
        return await get_realtime_data(stock_id)
    else:
        today = datetime.today().strftime("%Y%m%d")
        logger.info(f"[TWSE fallback] 市場已收????fallback ?�詢今日?��? ??{today}")
        return await get_historical_data(stock_id, today)
async def get_realtime_data(stock_id: str):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.twse.com.tw/"
    }

    logger.info(f"?�� [TWSE ?��?] ?�送查�???stock_id={stock_id}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10, follow_redirects=True)
            logger.info(f"[TWSE ?��?] ?��??�????{response.status_code}")
            data = response.json()
            logger.info(f"[TWSE ?��?] ?�傳 JSON：{data}")
        except Exception as e:
            logger.exception(f"[TWSE ?��?] ?�詢失�? ??{str(e)}")
            return {"error": "TWSE ?��??�詢?�誤，�?稍�??�試"}

    if not data.get("msgArray"):
        logger.warning(f"[TWSE ?��?] ?�無�?? ??{stock_id}，�??�內容�?{data}")
        return {"error": "?��??�股票代?��?請確認輸?�是?�正�?}

    info = data["msgArray"][0]
    logger.info(f"[TWSE ?��?] ?�交????{info.get('z')} ???�詢?��?")
    return {
        "資�?來�?": "?��??�詢",
        "?�票?�稱": info.get("n", ""),
        "?�票�??": info.get("c", ""),
        "?�交??: info.get("z", ""),
        "漲�?": info.get("y", ""),
        "?�收": info.get("y", ""),
        "?�盤": info.get("o", ""),
        "?�業??: info.get("ind", "N/A")
    }
async def get_historical_data(stock_id: str, date: str):
    logger.info(f"?�� [TWSE 歷史] ?�入歷史?�詢 ??stock_id={stock_id}, date={date}")

    try:
        original_query_date = datetime.strptime(str(date), "%Y%m%d")
    except ValueError:
        logger.warning(f"[TWSE 歷史] ?��??��??�誤 ??{date}")
        return {"error": "請使??YYYYMMDD ?��?輸入?��?（�?�?20250701�?}

    target_date = original_query_date
    retries = 7
    fallback_used = False

    for _ in range(retries):
        query_month = target_date.strftime("%Y%m")
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={query_month}01&stockNo={stock_id}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.twse.com.tw/",
            "Accept": "application/json"
        }

        logger.info(f"?�� [TWSE 歷史] ?�詢 ??stock_id={stock_id}, ??{query_month}, ?��???{target_date.strftime('%Y/%m/%d')}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10, follow_redirects=True)

                logger.info(f"[TWSE 歷史] ?��??�????{response.status_code}")
                content_type = response.headers.get("Content-Type", "N/A")
                logger.info(f"[TWSE 歷史] Content-Type ??{content_type}")
                raw_text = response.text
                logger.info(f"[TWSE 歷史] ?��? response.text ??{raw_text[:300]}")

                if response.status_code == 200 and "application/json" in content_type:
                    try:
                        data = response.json()
                        logger.info(f"[TWSE 歷史] ?�傳 JSON ??{data}")
                    except Exception as e:
                        logger.exception(f"[TWSE 歷史] JSON �???�誤 ??{str(e)}")
                        logger.info(f"[TWSE fallback] ?��? Goodinfo fallback")
                        return get_goodinfo_data(stock_id)
                else:
                    logger.warning(f"[TWSE 歷史] ??JSON ?��? ??Content-Type = {content_type}")
                    logger.info(f"[TWSE fallback] ?��? Goodinfo fallback")
                    return get_goodinfo_data(stock_id)

        except Exception as e:
            logger.exception(f"[TWSE 歷史] ?�叫失�? ??{str(e)}")
            return {"error": f"TWSE 歷史資�??��?失�?：{str(e)}"}

        twse_target_date = f"{target_date.year - 1911:03d}/{target_date.month:02d}/{target_date.day:02d}"

        for row in data.get("data", []):
            if isinstance(row, list) and row and row[0]:
                row_date_str = str(row[0]).strip()
                if row_date_str == twse_target_date:
                    logger.info(f"[TWSE 歷史] ?�交????{row[6]} ??資�?????{twse_target_date}")
                    result = {
                        "資�?來�?": "歷史?��?",
                        "?�票�??": stock_id,
                        "?�票?�稱": "?�詢結�?",
                        "?��??�詢?��?": original_query_date.strftime("%Y%m%d"),
                        "實�??�傳?��?": target_date.strftime("%Y%m%d"),
                        "?�盤": row[3],
                        "?��?: row[4],
                        "?��?: row[5],
                        "?�盤": row[6],
                        "?�交??: row[6],
                        "?�交??�?": row[1],
                    }
                    if fallback_used:
                        result["?�示"] = f"{original_query_date.strftime('%Y/%m/%d')} ?��?????已�?�?{target_date.strftime('%Y/%m/%d')} 資�?"
                    return result

        fallback_used = True
        target_date -= timedelta(days=1)

    logger.warning(f"[TWSE 歷史] {date} 起�???7 ?�查?��???)
    return {
        "error": f"{date} 起�???7 ?�查?�交?��??????�能?��???��??��??��???
    }
