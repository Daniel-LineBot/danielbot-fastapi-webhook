from fastapi import APIRouter, Query
import httpx
from typing import Optional, Union
from datetime import datetime, timedelta, time
from fastapi.logger import logger

router = APIRouter()

def is_twse_open():
    now = datetime.now().time()
    return time(9, 0) <= now <= time(13, 30)

@router.get("/stock/{stock_id}")
async def get_stock_info(stock_id: str, date: Optional[Union[str, None]] = Query(default=None)):
    logger.info("🪛 DanielBot stock.py ➜ 進入 get_stock_info handler")
    logger.info(f"📦 接收到 stock_id={stock_id}，date={repr(date)}")

    # 統一字串格式
    if date is not None and not isinstance(date, str):
        date = str(date)

    # 判斷是否為有效 date（非空）
    if date and date.strip():
        logger.info(f"[TWSE] 使用者指定查詢日期 ➜ {date.strip()} ➜ 查歷史資料")
        return await get_historical_data(stock_id, date.strip())

    # fallback 模式
    logger.info("🧭 未提供有效 date ➜ 進入 fallback 模式判斷 TWSE 是否開盤")
    now_time = datetime.now().strftime("%H:%M:%S")
    mode = "即時查詢" if is_twse_open() else "歷史查詢"
    logger.info(f"🧪 fallback 判斷 ➜ 時間：{now_time} ➜ 查詢模式：{mode}")

    if is_twse_open():
        return await get_realtime_data(stock_id)
    else:
        today = datetime.today().strftime("%Y%m%d")
        logger.info(f"[TWSE fallback] 已收盤 ➜ fallback 查詢今日盤後 ➜ {today}")
        return await get_historical_data(stock_id, today)


async def get_realtime_data(stock_id: str):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.twse.com.tw/"
    }

    logger.info(f"📡 呼叫即時 TWSE API ➜ stock_id={stock_id}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10)
            if "json" not in response.headers.get("content-type", "").lower():
                logger.warning(f"[TWSE 即時] 回傳非 JSON ➜ {response.text[:300]}")
                return {"error": "TWSE 即時查詢回傳非預期格式，請稍後再試或確認服務是否中斷"}
            data = response.json()
        except Exception as e:
            logger.exception(f"[TWSE 即時] API 查詢失敗 ➜ {str(e)}")
            return {"error": "TWSE 即時查詢發生錯誤，請稍後再試"}

    if not data.get("msgArray"):
        logger.warning(f"[TWSE 即時] 查無股票代號 ➜ {stock_id}")
        return {"error": "找不到股票代號，請確認輸入正確"}

    info = data["msgArray"][0]
    logger.info(f"[TWSE 即時] 成交價={info.get('z')} ➜ 完成即時查詢")

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
    logger.info(f"📦 進入歷史查詢 ➜ stock_id={stock_id}, date={date}")

    try:
        original_query_date = datetime.strptime(str(date), "%Y%m%d")
    except ValueError:
        logger.warning(f"[TWSE 歷史] 使用者輸入日期格式錯誤 ➜ {date}")
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
            "Referer": "https://www.twse.com.tw/"
        }

        logger.info(f"📡 嘗試查詢 TWSE 歷史資料 ➜ stock_id={stock_id}, query_month={query_month}, date={query_day}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
                content_type = response.headers.get("content-type", "")
                if "json" not in content_type.lower():
                    logger.warning(f"[TWSE 歷史] 非 JSON 回應 ➜ {response.text[:300]}")
                    return {"error": f"{date} 查詢失敗：TWSE 尚未釋出 {query_month} 月份資料"}
                data = response.json()
        except Exception as e:
            logger.exception(f"[TWSE 歷史] API 呼叫失敗 ➜ {str(e)}")
            return {"error": f"取得 TWSE 資料失敗：{str(e)}"}

        available_dates = [row[0] for row in data.get("data", []) if isinstance(row, list) and row]
        logger.info(f"[TWSE] {query_month} 資料日清單：{available_dates}")

        for row in data.get("data", []):
            if isinstance(row, list) and row and str(row[0]).startswith(query_day):
                actual_data_date = target_date.strftime("%Y%m%d")
                logger.info(f"[TWSE 歷史] 成交價={row[6]} ➜ 成功查詢 ➜ {actual_data_date}")
                result = {
                    "資料來源": "歷史盤後",
                    "股票代號": stock_id,
                    "原始查詢日期": original_query_date.strftime("%Y%m%d"),
                    "實際回傳日期": actual_data_date,
                    "開盤": row[3],
                    "最高": row[4],
                    "最低": row[5],
                    "收盤": row[6],
                    "成交量(張)": row[1],
                }
                if fallback_used:
                    result["提示"] = (
                        f"您查詢的 {original_query_date.strftime('%Y/%m/%d')} 無資料，"
                        f"已自動回覆 {target_date.strftime('%Y/%m/%d')} 的報價"
                    )
                return result

        fallback_used = True
        target_date -= timedelta(days=1)

    logger.warning(f"[TWSE 歷史] 起始日期 {date} 往前 7 日內查無資料")
    return {
        "error": f"{date} 起往前 7 日內查無任何交易紀錄（可能為連假或 TWSE 尚未釋出該月資料）"
    }
