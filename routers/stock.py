from fastapi import APIRouter, Query
import httpx
from typing import Optional
from datetime import datetime, timedelta
from fastapi.logger import logger  # 用於印 log 到 Cloud Run

router = APIRouter()

@router.get("/stock/{stock_id}")
async def get_stock_info(stock_id: str, date: Optional[str] = Query(default=None)):
    if date:
        return await get_historical_data(stock_id, date)
    else:
        return await get_realtime_data(stock_id)


async def get_realtime_data(stock_id: str):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

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
        target_date = datetime.strptime(date, "%Y%m%d")
    except ValueError:
        return {"error": "請使用 YYYYMMDD 格式輸入日期（例如 20250701）"}

    retries = 7
    for _ in range(retries):
        query_month = target_date.strftime("%Y%m")
        query_day = f"{target_date.year}/{target_date.month}/{target_date.day}"
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={query_month}01&stockNo={stock_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                content_type = response.headers.get("content-type", "")
                raw = response.text

                if "json" not in content_type:
                    logger.warning(f"[TWSE] {query_month} 回傳非 JSON，內容如下：{raw[:80]}...")
                    return {"error": f"{date} 查詢失敗：TWSE 尚未釋出該月份資料"}

                data = response.json()
        except Exception as e:
            return {"error": f"取得 TWSE 資料失敗：{str(e)}"}

        available_dates = [
            row[0] for row in data.get("data", [])
            if isinstance(row, list) and row
        ]
        logger.info(f"[TWSE] {query_month} 可用資料日：{available_dates}")

        for row in data.get("data", []):
            if isinstance(row, list) and row and str(row[0]).startswith(query_day):
                return {
                    "資料來源": "歷史盤後",
                    "股票代號": stock_id,
                    "查詢日期": target_date.strftime("%Y%m%d"),
                    "開盤": row[3],
                    "最高": row[4],
                    "最低": row[5],
                    "收盤": row[6],
                    "成交量(張)": row[1],
                }

        target_date -= timedelta(days=1)

    return {
        "error": f"{date} 起往前 7 日內查無任何交易紀錄（可能為連假或 TWSE 尚未釋出該月資料）"
    }
