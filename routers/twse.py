# routers/twse.py

import httpx
from bs4 import BeautifulSoup


async def get_twse_data(stock_id: str, date: str) -> dict:
    # TODO: 擷取 TWSE API 並解析資料
    return {
        "成交價": None,
        "開盤": None,
        "產業別": None
    }

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
