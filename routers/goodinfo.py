# routers/goodinfo.py

import httpx
from bs4 import BeautifulSoup


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
