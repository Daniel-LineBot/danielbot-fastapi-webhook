# routers/publicinfo.py

import httpx
from bs4 import BeautifulSoup

async def get_price_publicinfo(stock_id: str) -> dict:
    url = f"https://mops.twse.com.tw/mops/web/ajax_t05st10_ifrs"
    data = {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "true",
        "off": "1",
        "TYPEK": "sii",        # 上市公司
        "co_id": stock_id
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=data)
        soup = BeautifulSoup(resp.text, "html.parser")

        table = soup.find("table", class_="hasBorder")
        if not table:
            return {"error": "公開資訊觀測站無資料 ➜ fallback失敗"}

        rows = table.find_all("tr")[2:]  # 跳過表頭
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 5:
                return {
                    "資料時間": cells[0].text.strip(),
                    "股票名稱": cells[1].text.strip(),
                    "收盤": cells[2].text.strip(),
                    "漲跌幅": cells[3].text.strip(),
                    "成交量": cells[4].text.strip(),
                    "來源": "公開資訊觀測站"
                }

        return {"error": "資料解析失敗 ➜ fallback炸掉"}
