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
    text_raw = event.message.text.strip()
    text = text_raw.replace(" ", "")
    logger.info(f"[Webhook Text] 原始 ➜ {repr(text_raw)} ➜ 清理後 ➜ {repr(text)}")

    # ✅ 配息模組優先判斷
    if re.match(r"^配息\d{4}$", text):
        stock_id = re.sub(r"[^\d]", "", text)
        result = get_dividend_info(stock_id)
        if result.get("error"):
            reply_text = f"⚠️ {result['error']}"
        else:
            reply_text = (
                f"📦 {result['股票代號']} 配息資訊\n"
                f"年度：{result['配息年度']}\n"
                f"除權息日：{result['除權息日']}\n"
                f"現金股利：{result['現金股利']} 元\n"
                f"股票股利：{result['股票股利']} 股\n"
                f"發放日：{result['發放日']}\n"
                f"來源：{result['公告來源']}（{result['來源']}）\n"
                f"💡 {result['提示']}"
            )
        try:
            logger.info(f"[LINE回覆] ➜ {repr(reply_text)}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        except Exception as e:
            logger.exception(f"📛 回覆配息訊息失敗：{str(e)}")
        return  # ⛔️ 記得 return，避免進入查股 fallback

    # 📈 查股模組 ➜ 用你現有的查詢邏輯接在後面即可
    text = text_raw  # 你原本的查股模組就吃未清理的 text_raw
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
                f"成交價：{info.get('成交價', info.get('收盤', '-') )} 元\n"
                f"開盤：{info.get('開盤', '-') } 元\n"
                f"產業別：{info.get('產業別', info.get('資料來源', '-') )}"
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
            return "❗️日期格式錯誤，請使用 YYYYMMDD，例如：20250715"
        else:
            if date:
                datetime.strptime(date, "%Y%m%d")
                return await get_stock_info(stock_id, date)
            else:
                return await get_stock_info(stock_id)
    else:
        return (
            f"你剛說的是：{text}\n\n"
            "💡 指令範例：\n查詢 2330\n查詢 2330 20250715"
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

        # 股票名稱解析
        title = soup.title.string.strip()
        stock_name = title.split("(")[0].strip() if "(" in title else "未知"

        # 成交價解析
        price_tag = soup.select_one("#divPriceDetail .bg_h1")
        price = price_tag.text.strip() if price_tag else "查無"

        logger.info(f"[Goodinfo Fallback] 股票={stock_id} ➜ 成交價={price}")
        return {
            "資料來源": "Goodinfo fallback",
            "股票代號": stock_id,
            "股票名稱": stock_name,
            "成交價": price,
            "開盤": "-",
            "產業別": "N/A",
            "提示": "📦 TWSE 資料異常 ➜ 回傳 Goodinfo 查詢結果"
        }
    except Exception as e:
        logger.exception(f"[Goodinfo Fallback] 查詢失敗 ➜ {str(e)}")
        return {"error": f"Goodinfo fallback 查詢失敗：{str(e)}"}        
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
            data = response.json()
            logger.info(f"[TWSE 即時] 回傳 JSON：{data}")
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
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={query_month}01&stockNo={stock_id}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.twse.com.tw/",
            "Accept": "application/json"
        }

        logger.info(f"📡 [TWSE 歷史] 查詢 ➜ stock_id={stock_id}, 月={query_month}, 目標日={target_date.strftime('%Y/%m/%d')}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10, follow_redirects=True)

                logger.info(f"[TWSE 歷史] 回應狀態 ➜ {response.status_code}")
                content_type = response.headers.get("Content-Type", "N/A")
                logger.info(f"[TWSE 歷史] Content-Type ➜ {content_type}")
                raw_text = response.text
                logger.info(f"[TWSE 歷史] 原始 response.text ➜ {raw_text[:300]}")

                if response.status_code == 200 and "application/json" in content_type:
                    try:
                        data = response.json()
                        logger.info(f"[TWSE 歷史] 回傳 JSON ➜ {data}")
                    except Exception as e:
                        logger.exception(f"[TWSE 歷史] JSON 解析錯誤 ➜ {str(e)}")
                        logger.info(f"[TWSE fallback] 啟動 Goodinfo fallback")
                        return get_goodinfo_data(stock_id)
                else:
                    logger.warning(f"[TWSE 歷史] 非 JSON 回應 ➜ Content-Type = {content_type}")
                    logger.info(f"[TWSE fallback] 啟動 Goodinfo fallback")
                    return get_goodinfo_data(stock_id)

        except Exception as e:
            logger.exception(f"[TWSE 歷史] 呼叫失敗 ➜ {str(e)}")
            return {"error": f"TWSE 歷史資料取得失敗：{str(e)}"}

        twse_target_date = f"{target_date.year - 1911:03d}/{target_date.month:02d}/{target_date.day:02d}"

        for row in data.get("data", []):
            if isinstance(row, list) and row and row[0]:
                row_date_str = str(row[0]).strip()
                if row_date_str == twse_target_date:
                    logger.info(f"[TWSE 歷史] 成交價 ➜ {row[6]} ➜ 資料日 ➜ {twse_target_date}")
                    result = {
                        "資料來源": "歷史盤後",
                        "股票代號": stock_id,
                        "股票名稱": "查詢結果",
                        "原始查詢日期": original_query_date.strftime("%Y%m%d"),
                        "實際回傳日期": target_date.strftime("%Y%m%d"),
                        "開盤": row[3],
                        "最高": row[4],
                        "最低": row[5],
                        "收盤": row[6],
                        "成交價": row[6],
                        "成交量(張)": row[1],
                    }
                    if fallback_used:
                        result["提示"] = f"{original_query_date.strftime('%Y/%m/%d')} 無資料 ➜ 已回覆 {target_date.strftime('%Y/%m/%d')} 資料"
                    return result

        fallback_used = True
        target_date -= timedelta(days=1)

    logger.warning(f"[TWSE 歷史] {date} 起往前 7 日查無資料")
    return {
        "error": f"{date} 起往前 7 日查無交易紀錄 ➜ 可能遇連假或尚未釋出資料"
    }
def get_dividend_info(stock_id: str):
    url = f"https://goodinfo.tw/tw/StockDividendPolicy.asp?STOCK_ID={stock_id}&STEP=DATA"
    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://goodinfo.tw/"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        return {"error": f"無法連線到 Goodinfo：{str(e)}"}

    table = (
        soup.select_one("table.b1.p4_2.r10.box_shadow")
        or soup.select_one("table.b1.p4_2.r10")
    )

    if not table:
        return {"error": f"查無 {stock_id} 的配息表格，可能網站結構已變"}

    rows = table.select("tr")[1:]
    latest_row = None
    this_year = str(datetime.now().year)

    for row in rows:
        cols = [td.get_text(strip=True) for td in row.select("td")]
        if len(cols) >= 10 and cols[0].startswith(this_year):
            latest_row = cols
            break

    if not latest_row and rows:
        latest_row = [td.get_text(strip=True) for td in rows[0].select("td")]
        note = "查無今年資料，回傳最近一筆紀錄"
    elif latest_row:
        note = "查詢成功"
    else:
        return {"error": "找不到任何可用的配息資料"}
        
    # 如果你已經在 stock.py，可直接呼叫自己內部函式
    stock_info = get_stock_info(stock_id)
    stock_name = stock_info.get("股票名稱", "N/A")
    return {
        "股票代號": stock_id,
        "股票名稱": stock_name,  ✅ 才能讓 callback 顯示正常的名稱
        "配息年度": latest_row[0],
        "除權息日": latest_row[3],
        "現金股利": latest_row[4],
        "股票股利": latest_row[5],
        "發放日": latest_row[6],
        "來源": latest_row[8],
        "公告來源": "Goodinfo",
        "提示": note
    }
