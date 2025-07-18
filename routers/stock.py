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
        logger.warning("??LINE Webhook Signature é©—è?å¤±æ?")
        return "Invalid signature", 400
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent):
    text_raw = event.message.text.strip()
    text = text_raw.replace(" ", "")
    logger.info(f"[Webhook Text] ?Ÿå? ??{repr(text_raw)} ??æ¸…ç?å¾???{repr(text)}")

    # ???æ¯æ¨¡ç??ªå??¤æ–·
    if re.match(r"^?æ¯\d{4}$", text):
        stock_id = re.sub(r"[^\d]", "", text)
        result = get_dividend_info(stock_id)
        if result.get("error"):
            reply_text = f"? ï? {result['error']}"
        else:
            reply_text = (
                f"?“¦ {result['?¡ç¥¨ä»??']} ?æ¯è³‡è?\n"
                f"å¹´åº¦ï¼š{result['?æ¯å¹´åº¦']}\n"
                f"?¤æ??¯æ—¥ï¼š{result['?¤æ??¯æ—¥']}\n"
                f"?¾é??¡åˆ©ï¼š{result['?¾é??¡åˆ©']} ?ƒ\n"
                f"?¡ç¥¨?¡åˆ©ï¼š{result['?¡ç¥¨?¡åˆ©']} ?¡\n"
                f"?¼æ”¾?¥ï?{result['?¼æ”¾??]}\n"
                f"ä¾†æ?ï¼š{result['?¬å?ä¾†æ?']}ï¼ˆ{result['ä¾†æ?']}ï¼‰\n"
                f"?’¡ {result['?ç¤º']}"
            )
        try:
            logger.info(f"[LINE?è?] ??{repr(reply_text)}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        except Exception as e:
            logger.exception(f"?? ?è??æ¯è¨Šæ¯å¤±æ?ï¼š{str(e)}")
        return  # ?”ï? è¨˜å? returnï¼Œé¿?é€²å…¥?¥è‚¡ fallback

    # ?? ?¥è‚¡æ¨¡ç? ???¨ä??¾æ??„æŸ¥è©¢é?è¼¯æ¥?¨å??¢å³??    text = text_raw  # ä½ å??¬ç??¥è‚¡æ¨¡ç?å°±å??ªæ??†ç? text_raw
    reply_text = ""
    try:
        info = asyncio.run(get_response_info(text))
        if isinstance(info, str):
            reply_text = info
        elif info.get("error"):
            reply_text = f"? ï? {info['error']}"
        elif info.get("?äº¤??) or info.get("?¶ç›¤"):
            reply_text = (
                f"?? {info.get('?¡ç¥¨?ç¨±', '')}ï¼ˆ{info.get('?¡ç¥¨ä»??', '')}ï¼‰\n"
                f"?äº¤?¹ï?{info.get('?äº¤??, info.get('?¶ç›¤', '-') )} ?ƒ\n"
                f"?‹ç›¤ï¼š{info.get('?‹ç›¤', '-') } ?ƒ\n"
                f"?¢æ¥­?¥ï?{info.get('?¢æ¥­??, info.get('è³‡æ?ä¾†æ?', '-') )}"
            )
            if info.get("?ç¤º"):
                reply_text += f"\n?’¡ {info['?ç¤º']}"
        else:
            reply_text = "? ï? ?¥ç„¡è³‡æ?ï¼Œè?ç¢ºè??¡ç¥¨ä»???–æ—¥?Ÿæ˜¯?¦æ­£ç¢?
    except Exception as e:
        logger.exception(f"?? ?¥è‚¡ä¾‹å?ï¼š{str(e)}")
        reply_text = f"? ï? ?¥è©¢?‚ç™¼?ŸéŒ¯èª¤ï?{str(e)}"

    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    except Exception as e:
        logger.exception(f"?? ?è?è¨Šæ¯å¤±æ?ï¼š{str(e)}")
async def get_response_info(text: str):
    if text.startswith("?¥è©¢"):
        args = text.replace("?¥è©¢", "").strip().split()
        stock_id = args[0] if len(args) >= 1 else ""
        date = args[1] if len(args) >= 2 else None

        if not re.fullmatch(r"\d{4}", stock_id):
            return "?—ï?è«‹è¼¸?¥æ­£ç¢ºç??›ä??¸è‚¡ç¥¨ä»£?Ÿï?ä¾‹å?ï¼šæŸ¥è©?2330"
        elif date and not re.fullmatch(r"\d{8}", date):
            return "?—ï??¥æ??¼å??¯èª¤ï¼Œè?ä½¿ç”¨ YYYYMMDDï¼Œä?å¦‚ï?20250715"
        else:
            if date:
                datetime.strptime(date, "%Y%m%d")
                return await get_stock_info(stock_id, date)
            else:
                return await get_stock_info(stock_id)
    else:
        return (
            f"ä½ å?èªªç??¯ï?{text}\n\n"
            "?’¡ ?‡ä»¤ç¯„ä?ï¼š\n?¥è©¢ 2330\n?¥è©¢ 2330 20250715"
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

        # ?¡ç¥¨?ç¨±è§??
        title = soup.title.string.strip()
        stock_name = title.split("(")[0].strip() if "(" in title else "?ªçŸ¥"

        # ?äº¤?¹è§£??        price_tag = soup.select_one("#divPriceDetail .bg_h1")
        price = price_tag.text.strip() if price_tag else "?¥ç„¡"

        logger.info(f"[Goodinfo Fallback] ?¡ç¥¨={stock_id} ???äº¤??{price}")
        return {
            "è³‡æ?ä¾†æ?": "Goodinfo fallback",
            "?¡ç¥¨ä»??": stock_id,
            "?¡ç¥¨?ç¨±": stock_name,
            "?äº¤??: price,
            "?‹ç›¤": "-",
            "?¢æ¥­??: "N/A",
            "?ç¤º": "?“¦ TWSE è³‡æ??°å¸¸ ???å‚³ Goodinfo ?¥è©¢çµæ?"
        }
    except Exception as e:
        logger.exception(f"[Goodinfo Fallback] ?¥è©¢å¤±æ? ??{str(e)}")
        return {"error": f"Goodinfo fallback ?¥è©¢å¤±æ?ï¼š{str(e)}"}        
async def get_stock_info(stock_id: str, date: Optional[Union[str, None]] = None):
    logger.info("?? DanielBot stock.py ??å·²å???get_stock_info handler")
    logger.info(f"?“¦ ?³å…¥ stock_id={stock_id}, date={repr(date)}")

    if date and not isinstance(date, str):
        date = str(date)

    if date and date.strip():
        logger.info(f"?§® ä½¿ç”¨?…æ?å®šæ—¥????{date.strip()} ???Ÿç”¨ get_historical_data()")
        return await get_historical_data(stock_id, date.strip())

    logger.info("?§­ ?ªæ?ä¾›æ???date ???Ÿç”¨ fallback ?¤æ–·")
    now_time = datetime.now().strftime("%H:%M:%S")
    mode = "?³æ??¥è©¢" if is_twse_open() else "æ­·å²?¥è©¢"
    logger.info(f"?§ª fallback ?¤æ–· ???¾åœ¨?‚é?ï¼š{now_time} ??æ¨¡å?ï¼š{mode}")

    if is_twse_open():
        return await get_realtime_data(stock_id)
    else:
        today = datetime.today().strftime("%Y%m%d")
        logger.info(f"[TWSE fallback] å¸‚å ´å·²æ”¶????fallback ?¥è©¢ä»Šæ—¥?¤å? ??{today}")
        return await get_historical_data(stock_id, today)
async def get_realtime_data(stock_id: str):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.twse.com.tw/"
    }

    logger.info(f"?“¡ [TWSE ?³æ?] ?¼é€æŸ¥è©???stock_id={stock_id}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10, follow_redirects=True)
            logger.info(f"[TWSE ?³æ?] ?æ??€????{response.status_code}")
            data = response.json()
            logger.info(f"[TWSE ?³æ?] ?å‚³ JSONï¼š{data}")
        except Exception as e:
            logger.exception(f"[TWSE ?³æ?] ?¥è©¢å¤±æ? ??{str(e)}")
            return {"error": "TWSE ?³æ??¥è©¢?¯èª¤ï¼Œè?ç¨å??è©¦"}

    if not data.get("msgArray"):
        logger.warning(f"[TWSE ?³æ?] ?¥ç„¡ä»?? ??{stock_id}ï¼Œå??³å…§å®¹ï?{data}")
        return {"error": "?¾ä??°è‚¡ç¥¨ä»£?Ÿï?è«‹ç¢ºèªè¼¸?¥æ˜¯?¦æ­£ç¢?}

    info = data["msgArray"][0]
    logger.info(f"[TWSE ?³æ?] ?äº¤????{info.get('z')} ???¥è©¢?å?")
    return {
        "è³‡æ?ä¾†æ?": "?³æ??¥è©¢",
        "?¡ç¥¨?ç¨±": info.get("n", ""),
        "?¡ç¥¨ä»??": info.get("c", ""),
        "?äº¤??: info.get("z", ""),
        "æ¼²è?": info.get("y", ""),
        "?¨æ”¶": info.get("y", ""),
        "?‹ç›¤": info.get("o", ""),
        "?¢æ¥­??: info.get("ind", "N/A")
    }
async def get_historical_data(stock_id: str, date: str):
    logger.info(f"?“¦ [TWSE æ­·å²] ?²å…¥æ­·å²?¥è©¢ ??stock_id={stock_id}, date={date}")

    try:
        original_query_date = datetime.strptime(str(date), "%Y%m%d")
    except ValueError:
        logger.warning(f"[TWSE æ­·å²] ?¥æ??¼å??¯èª¤ ??{date}")
        return {"error": "è«‹ä½¿??YYYYMMDD ?¼å?è¼¸å…¥?¥æ?ï¼ˆä?å¦?20250701ï¼?}

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

        logger.info(f"?“¡ [TWSE æ­·å²] ?¥è©¢ ??stock_id={stock_id}, ??{query_month}, ?®æ???{target_date.strftime('%Y/%m/%d')}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10, follow_redirects=True)

                logger.info(f"[TWSE æ­·å²] ?æ??€????{response.status_code}")
                content_type = response.headers.get("Content-Type", "N/A")
                logger.info(f"[TWSE æ­·å²] Content-Type ??{content_type}")
                raw_text = response.text
                logger.info(f"[TWSE æ­·å²] ?Ÿå? response.text ??{raw_text[:300]}")

                if response.status_code == 200 and "application/json" in content_type:
                    try:
                        data = response.json()
                        logger.info(f"[TWSE æ­·å²] ?å‚³ JSON ??{data}")
                    except Exception as e:
                        logger.exception(f"[TWSE æ­·å²] JSON è§???¯èª¤ ??{str(e)}")
                        logger.info(f"[TWSE fallback] ?Ÿå? Goodinfo fallback")
                        return get_goodinfo_data(stock_id)
                else:
                    logger.warning(f"[TWSE æ­·å²] ??JSON ?æ? ??Content-Type = {content_type}")
                    logger.info(f"[TWSE fallback] ?Ÿå? Goodinfo fallback")
                    return get_goodinfo_data(stock_id)

        except Exception as e:
            logger.exception(f"[TWSE æ­·å²] ?¼å«å¤±æ? ??{str(e)}")
            return {"error": f"TWSE æ­·å²è³‡æ??–å?å¤±æ?ï¼š{str(e)}"}

        twse_target_date = f"{target_date.year - 1911:03d}/{target_date.month:02d}/{target_date.day:02d}"

        for row in data.get("data", []):
            if isinstance(row, list) and row and row[0]:
                row_date_str = str(row[0]).strip()
                if row_date_str == twse_target_date:
                    logger.info(f"[TWSE æ­·å²] ?äº¤????{row[6]} ??è³‡æ?????{twse_target_date}")
                    result = {
                        "è³‡æ?ä¾†æ?": "æ­·å²?¤å?",
                        "?¡ç¥¨ä»??": stock_id,
                        "?¡ç¥¨?ç¨±": "?¥è©¢çµæ?",
                        "?Ÿå??¥è©¢?¥æ?": original_query_date.strftime("%Y%m%d"),
                        "å¯¦é??å‚³?¥æ?": target_date.strftime("%Y%m%d"),
                        "?‹ç›¤": row[3],
                        "?€é«?: row[4],
                        "?€ä½?: row[5],
                        "?¶ç›¤": row[6],
                        "?äº¤??: row[6],
                        "?äº¤??å¼?": row[1],
                    }
                    if fallback_used:
                        result["?ç¤º"] = f"{original_query_date.strftime('%Y/%m/%d')} ?¡è?????å·²å?è¦?{target_date.strftime('%Y/%m/%d')} è³‡æ?"
                    return result

        fallback_used = True
        target_date -= timedelta(days=1)

    logger.warning(f"[TWSE æ­·å²] {date} èµ·å???7 ?¥æŸ¥?¡è???)
    return {
        "error": f"{date} èµ·å???7 ?¥æŸ¥?¡äº¤?“ç??????¯èƒ½?‡é€???–å??ªé??ºè???
    }
