# routers/goodinfo.py

import httpx
from bs4 import BeautifulSoup

async def get_price_goodinfo(stock_id: str) -> dict:
    url = f"https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID={stock_id}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://goodinfo.tw"
    }
    
    timeout = httpx.Timeout(5.0)  # 加在 headers 下方
    
    async with httpx.AsyncClient(headers=headers) as client:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", class_="b1 p4_2 r_frame")

        if not table:
            return {"error": "Goodinfo 無資料 ➜ fallback失敗"}

        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 6:
                return {
                    "資料時間": cells[0].text.strip(),
                    "股票名稱": cells[1].text.strip(),
                    "收盤": cells[2].text.strip(),
                    "漲跌幅": cells[3].text.strip(),
                    "成交量": cells[4].text.strip(),
                    "來源": "Goodinfo"
                }

        return {"error": "Goodinfo 資料解析失敗"}



"""
async def get_goodinfo_metadata(stock_id: str) -> dict:
    # TODO: 使用 aiohttp 抓取網頁、lxml 或 bs4 分析 HTML
    return {
        "本益比": None,
        "殖利率": None,
        "股利政策": None
    }


async def get_price_goodinfo(stock_id: str) -> dict:
    url = f"https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={stock_id}"
    headers = {"user-agent": "Mozilla/5.0"}

    async with httpx.AsyncClient(headers=headers) as client:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        box = soup.select_one("#divPriceDetail")
        if not box:
            return {"error": "Goodinfo查詢失敗 ➜ 找不到價格區塊"}

        rows = box.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if any("成交" in cell.text for cell in cells):
                result = {
                    "股票代號": stock_id,
                    "收盤": cells[1].text.strip(),
                    "漲跌": cells[3].text.strip(),
                    "成交量": cells[5].text.strip(),
                    "資料時間": cells[7].text.strip(),
                    "來源": "Goodinfo"
                }
                return result

        return {"error": "Goodinfo解析失敗 ➜ fallback炸掉"}
"""
