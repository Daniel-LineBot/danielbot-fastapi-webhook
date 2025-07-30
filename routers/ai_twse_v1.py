#routers/ai_twse_v1.py
import httpx
from loguru import logger
from utils.formatter_twse import format_dividend
import re
from utils.stock_parser import extract_ex_date_from_note


async def get_twse_price(stock_id: str, date: str = None) -> dict:
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            data = r.json()

            # 🔍 Schema trace: 確認 key 結構是否如預期
            logger.warning(f"[TWSE Price] Total records: {len(data)}")
            if len(data) > 0:
                logger.warning(f"[TWSE Price] First record keys: {list(data[0].keys())}")

            for item in data:
                if item.get("證券代號") == stock_id:
                    return {
                        "name": item.get("證券名稱", "-"),
                        "price": item.get("收盤價", "-"),
                        "open": item.get("開盤價", "-"),
                        "high": item.get("最高價", "-"),
                        "low": item.get("最低價", "-"),
                        "volume": item.get("成交股數", "-"),
                        "date": item.get("日期", "-"),
                        "source": "TWSE"
                    }

        except Exception as e:
            logger.warning(f"[TWSE Price] API 讀取失敗: {e}")
            return {"error": str(e)}

    return {"error": f"TWSE 查無股價資料 for {stock_id}"}


async def get_twse_dividend(stock_id: str) -> dict:
    url = "https://openapi.twse.com.tw/v1/opendata/t187ap45_L"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            data = r.json()

            logger.warning(f"[TWSE Dividend] Total records: {len(data)}")
            if len(data) > 0:
                logger.warning(f"[TWSE Dividend] First record keys: {list(data[0].keys())}")

            for item in data:
                if item.get("公司代號") == stock_id:
                    note = item.get("備註", "")
                    ex_date = extract_ex_date_from_note(note) or item.get("出表日期", "-")

                    dividend = {
                        "year": item.get("股利年度", "-"),
                        "cash_dividend": item.get("股東配發-盈餘分配之現金股利(元/股)", "-"),
                        "stock_dividend": item.get("股東配發-盈餘轉增資配股(元/股)", "-"),
                        "ex_dividend_date": ex_date,
                        "source": "TWSE"
                    }

                    return {"text": format_dividend(dividend), **dividend}

        except Exception as e:
            logger.warning(f"[TWSE Dividend] API 讀取失敗: {e}")
            return {"error": str(e)}

    return {"error": f"TWSE 查無配息資料 for {stock_id}"}
