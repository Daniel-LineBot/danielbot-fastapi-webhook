from fastapi import APIRouter, Query
import httpx
from typing import Optional
from datetime import datetime, timedelta

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
        "股票名稱": info["n"],
        "股票代號": info["c"],
        "成交價": info["z"],
        "漲跌": info["y"],
        "昨收": info["y"],
        "開盤": info["o"],
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
        query_day_str = f"{target_date.year}/{target_date.month}/{target_date.day}"
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={query_month}01&stockNo={stock_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        if "data" in data and data["data"]:
            for row in data["data"]:
                if row[0].startswith(query_day_str):
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
        "error": f"{date} 起往前 7 日內查無任何交易紀錄，可能為連續假日或 TWSE 尚未釋出資料"
    }


