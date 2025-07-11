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
    # ⚠️ 修復：確認 date 是字串
    if date is not None and not isinstance(date, str):
        date = str(date)

    if date:
        return await get_historical_data(stock_id, date)

    # ✅ 無 date 時，自動根據時間決定查詢模式
    if is_twse_open():
        logger.info(f"[TWSE 判斷] 開盤中 ➜ 查即時")
        return await get_realtime_data(stock_id)
    else:
        today = datetime.today().strftime("%Y%m%d")
        logger.info(f"[TWSE 判斷] 已收盤 ➜ 查 {today} 歷史資料")
        return await get_historical_data(stock_id, today)


async def get_realtime_data(stock_id: str):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.twse.com.tw/"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10)
            if "json" not in response.headers.get("content-type", "").lower():
                logger.error(f"[TWSE 即時] 非 JSON 回應：{response.text[:300]}")
                return {"error": "TWSE 即時查詢回傳非預期格式，請稍後再試或確認服務是否中斷"}

            data = response.json()
        except Exception as e:
            logger.exception(f"[TWSE 即時] 資料解析失敗：{str(e)}")
            return {"error": "TWSE 即時查詢發生錯誤，請稍後再試"}

    if not data.get("msgArray"):
        return {"error": "找不到股票代號，請確認輸入正確"}

    info = data["msgArray"][0]
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
    try:
        original_query_date = datetime.strptime(str(date), "%Y%m%d")  # ✅ 強制轉字串處理 Query 物件
    except ValueError:
        return {"error": "請使用 YYYYMMDD 格式輸入日期（例如 20250701）"}

    target_date = original_query_date
    retries = 7
    fallback_used = False
    actual_data_date = None

    for _ in range(retries):
        query_month = target_date.strftime("%Y%m")
        query_day = f"{target_date.year}/{target_date.month}/{target_date.day}"
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={query_month}01&stockNo={stock_id}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.twse.com.tw/"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
                content_type = response.headers.get("content-type", "")
                if "json" not in content_type.lower():
                    logger.warning(f"[TWSE 歷史] 回傳非 JSON：{response.text[:300]}")
                    return {"error": f"{date} 查詢失敗：TWSE 尚未釋出 {query_month} 月份資料"}

                data = response.json()
        except Exception as e:
            logger.exception(f"[TWSE 歷史] 資料取得失敗：{str(e)}")
            return {"error": f"取得 TWSE 資料失敗：{str(e)}"}

        available_dates = [
            row[0] for row in data.get("data", [])
            if isinstance(row, list) and row
        ]
        logger.info(f"[TWSE] {query_month} 可用資料日：{available_dates}")

        for row in data.get("data", []):
            if isinstance(row, list) and row and str(row[0]).startswith(query_day):
                actual_data_date = target_date.strftime("%Y%m%d")
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

    return {
        "error": f"{date} 起往前 7 日內查無任何交易紀錄（可能為連假或 TWSE 尚未釋出該月資料）"
    }
