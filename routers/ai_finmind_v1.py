import os
import httpx 

FINMIND_TOKEN = os.getenv("FINMIND_TOKEN")

async def get_finmind_price(stock_id: str, date: str = None) -> dict:
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": stock_id,
        "token": FINMIND_TOKEN
    }
    if date:
        params["start_date"] = date
        params["end_date"] = date

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        data = r.json().get("data", [])
        if data:
            latest = data[-1]
            return {
                "name": latest.get("stock_id"),
                "price": latest.get("close"),
                "open": latest.get("open"),
                "high": latest.get("max"),
                "low": latest.get("min"),
                "volume": latest.get("Trading_Volume"),
                "date": latest.get("date"),
                "source": "FinMind"
            }
        return {"error": "查無資料"}

async def get_finmind_dividend(stock_id: str) -> dict:
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanStockDividend",
        "data_id": stock_id,
        "token": FINMIND_TOKEN
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        data = r.json().get("data", [])
        if data:
            latest = data[-1]
            return {
                "year": latest.get("year"),
                "cash_dividend": latest.get("cash_dividend"),
                "stock_dividend": latest.get("stock_dividend"),
                "ex_dividend_date": latest.get("ex_dividend_trading_date"),
                "source": "FinMind"
            }
        return {"error": "查無配息資料"}
