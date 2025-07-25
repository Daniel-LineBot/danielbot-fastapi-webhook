# routers/twse.py

import httpx
from bs4 import BeautifulSoup

from datetime import datetime, timedelta, date
import calendar


import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

async def get_twse_data(stock_id: str, date: str = "") -> dict:
    url = "https://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html"
    date_to_use = date or datetime.today().strftime("%Y%m%d")
    params = {
        "response": "html",
        "date": date_to_use,
        "stockNo": stock_id,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")[2:] if table else []

        # 🧨 fallback: 表格空就查昨天
        if not rows and not date:
            yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
            params["date"] = yesterday
            resp = await client.get(url, params=params)
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table")
            rows = table.find_all("tr")[2:] if table else []

        if not rows:
            return {"error": "TWSE查詢失敗 ➜ 找不到資料或資料為空"}

        for row in reversed(rows):
            cells = row.find_all("td")
            if len(cells) >= 7:
                return {
                    "資料時間": cells[0].text.strip(),
                    "開盤": cells[1].text.strip(),
                    "最高": cells[2].text.strip(),
                    "最低": cells[3].text.strip(),
                    "收盤": cells[4].text.strip(),
                    "漲跌": cells[5].text.strip(),
                    "成交量": cells[6].text.strip(),
                    "來源": "TWSE",
                }

        return {"error": "TWSE無法解析最新成交資料"}

async def get_price_twse(stock_id: str) -> dict:
    url = f"https://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html"
    params = {
        "response": "html",
        "date": "",
        "stockNo": stock_id
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        soup = BeautifulSoup(resp.text, "html.parser")

        table = soup.find("table")
        if not table:
            return {"error": "TWSE查詢失敗 ➜ 找不到資料表"}

        rows = table.find_all("tr")[2:]  # 跳過表頭
        latest = None
        for row in reversed(rows):
            cells = row.find_all("td")
            if len(cells) >= 7:
                latest = {
                    "資料時間": cells[0].text.strip(),
                    "開盤": cells[1].text.strip(),
                    "最高": cells[2].text.strip(),
                    "最低": cells[3].text.strip(),
                    "收盤": cells[4].text.strip(),
                    "漲跌": cells[5].text.strip(),
                    "成交量": cells[6].text.strip(),
                    "來源": "TWSE"
                }
                break

        return latest or {"error": "TWSE無法解析最新成交資料"}


"""
async def get_twse_data(stock_id: str, date: str = "", use_json: bool = False) -> dict:
    if use_json:
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        date_to_use = date or datetime.today().strftime("%Y%m%d")
        params = {
            "response": "json",
            "date": date_to_use,
            "stockNo": stock_id,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            json_data = resp.json()
            rows = json_data.get("data", [])

            # ⏪ fallback 查昨天
            if not rows and not date:
                yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
                params["date"] = yesterday
                resp = await client.get(url, params=params)
                json_data = resp.json()
                rows = json_data.get("data", [])

            if not rows:
                return {"error": "TWSE JSON查詢失敗 ➜ 找不到資料"}

            last_row = rows[-1]
            return {
                "資料時間": json_data.get("date", date_to_use),
                "開盤": last_row[3],
                "最高": last_row[4],
                "最低": last_row[5],
                "收盤": last_row[6],
                "漲跌": last_row[7],
                "成交量": last_row[1],
                "來源": "TWSE_JSON"
            }

    # 🔁 fallback: TWSE HTML
    url = "https://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html"
    date_to_use = date or datetime.today().strftime("%Y%m%d")
    params = {
        "response": "html",
        "date": date_to_use,
        "stockNo": stock_id,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")[2:] if table else []

        # 🧨 fallback 查昨天
        if not rows and not date:
            yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
            params["date"] = yesterday
            resp = await client.get(url, params=params)
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table")
            rows = table.find_all("tr")[2:] if table else []

        if not rows:
            return {"error": "TWSE HTML查詢失敗 ➜ 找不到資料或資料為空"}

        for row in reversed(rows):
            cells = row.find_all("td")
            if len(cells) >= 7:
                return {
                    "資料時間": cells[0].text.strip(),
                    "開盤": cells[1].text.strip(),
                    "最高": cells[2].text.strip(),
                    "最低": cells[3].text.strip(),
                    "收盤": cells[4].text.strip(),
                    "漲跌": cells[5].text.strip(),
                    "成交量": cells[6].text.strip(),
                    "來源": "TWSE",
                }

        return {"error": "TWSE HTML無法解析最新成交資料"}
"""


