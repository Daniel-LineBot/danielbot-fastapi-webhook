from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import datetime

async def get_dividend_info(stock_id: str):
    url = f"https://goodinfo.tw/tw/StockDividendPolicy.asp?STOCK_ID={stock_id}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "referer": "https://goodinfo.tw/"
    }

    session = AsyncHTMLSession()
    try:
        r = await session.get(url, headers=headers)
        soup = BeautifulSoup(r.html.html, "html.parser")
    except Exception as e:
        await session.close()
        return {"error": f"無法連線到 Goodinfo：{str(e)}"}

    await session.close()

    # 嘗試抓配息表格 ➜ selector fallback
    table = (
        soup.select_one("table.b1.p4_2.r10.box_shadow")
        or soup.select_one("table.b1.p4_2.r10")
    )

    if not table:
        return {"error": f"查無 {stock_id} 的配息表格，可能網站結構已變"}

    rows = table.select("tr")
    data_rows = rows[1:]

    latest_row = None
    this_year = str(datetime.datetime.now().year)

    for row in data_rows:
        cols = [td.get_text(strip=True) for td in row.select("td")]
        if len(cols) >= 10 and cols[0].startswith(this_year):
            latest_row = cols
            break

    if not latest_row and data_rows:
        latest_row = [td.get_text(strip=True) for td in data_rows[0].select("td")]
        note = "查無今年資料，回傳最近一筆紀錄"
    elif latest_row:
        note = "查詢成功"
    else:
        return {"error": "找不到任何可用的配息資料"}

    return {
        "股票代號": stock_id,
        "配息年度": latest_row[0],
        "除權息日": latest_row[3],
        "現金股利": latest_row[4],
        "股票股利": latest_row[5],
        "發放日": latest_row[6],
        "來源": latest_row[8],
        "公告來源": "Goodinfo",
        "提示": note
    }


    
