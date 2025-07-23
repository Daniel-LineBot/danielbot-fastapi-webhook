# routers/goodinfo.py
import httpx
import re
from loguru import logger

#from yfinance import Ticker # For Yahoo 即時成交價



GOODINFO_URL = "https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID={stock_id}"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://goodinfo.tw/",
    "Accept": "text/html"
}


async def get_goodinfo_price_robust(stock_id: str) -> dict:
    """
    fallback Goodinfo 查成交價 ➜ 改用 <th>成交</th><td>xx.xx</td> 結構 ➕ title 備援
    """
    stock_id = str(stock_id).strip()
    url = GOODINFO_URL.format(stock_id=stock_id)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            html = response.text

            # ✅ 方法 1 ➜ <th>成交</th><td>xx.xx</td>
            th_match = re.search(r"<th[^>]*?>\s*成交\s*</th>\s*<td[^>]*?>([\d,.]+)</td>", html, re.IGNORECASE)
            if th_match:
                price = th_match.group(1).replace(",", "").strip()
                logger.info(f"📦 [th] Goodinfo 成交價 ➜ {stock_id} ➜ {price}")
                return {"price": price}

            # ✅ 方法 2 ➜ legacy title 解析備援
            legacy_match = re.search(r"成交價[:：]\s*([\d,]+\.?\d*)", html)
            if legacy_match:
                price = legacy_match.group(1).replace(",", "").strip()
                logger.info(f"📦 [title] fallback 成交價 ➜ {stock_id} ➜ {price}")
                return {"price": price}

            logger.warning(f"⚠️ Goodinfo 未找到成交價 ➜ stock_id={stock_id}")
            return {"price": "查無"}

    except Exception as e:
        logger.exception(f"❌ fallback Goodinfo 查成交價失敗 ➜ {str(e)}")
        return {"price": "查無"}


async def get_goodinfo_price(stock_id: str) -> dict:
    """
    fallback Goodinfo 查歷史價格 ➜ 回傳 {'price': xx.xx}
    """
    stock_id = str(stock_id).strip()
    url = f"https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID={stock_id}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://goodinfo.tw/",
        "Accept": "text/html"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            html = response.text

            # 🔍 擷取成交價 ➜ 假設存在 "成交價：858 元"
            match = re.search(r"成交價[:：]\s*([\d,]+\.?\d*)", html)
            if match:
                price = match.group(1).replace(",", "").strip()
                logger.info(f"📦 Goodinfo 成交價 ➜ {stock_id} ➜ {price}")
                return {"price": price}
            else:
                logger.warning(f"⚠️ Goodinfo 未找到成交價 ➜ stock_id={stock_id}")
                return {"price": "查無"}

    except Exception as e:
        logger.exception(f"❌ Goodinfo 查價失敗 ➜ {str(e)}")
        return {"price": "查無"}

async def get_goodinfo_name(stock_id: str) -> str:
    """
    從 Goodinfo 查詢股票名稱 ➜ 例如 2330 ➜ 台積電
    """
    stock_id = str(stock_id).strip()
    url = GOODINFO_URL.format(stock_id=stock_id)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            html = response.text

            # 🔍 從 <title> 擷取名稱 ➜ 台積電 (2330)
            match = re.search(r"<title>(.*?)\s+\(" + stock_id + r"\)</title>", html)
            if match:
                name = match.group(1).strip()
                logger.info(f"📦 Goodinfo 查名稱成功 ➜ {stock_id} ➜ {name}")
                return name
            else:
                logger.warning(f"⚠️ Goodinfo 無法解析名稱 ➜ stock_id={stock_id}")
                return "查無"
    except Exception as e:
        logger.exception(f"❌ Goodinfo 查名稱失敗 ➜ {str(e)}")
        return "查無"

async def get_goodinfo_industry(stock_id: str) -> str:
    """
    從 Goodinfo 查詢產業分類 ➜ 例如 2330 ➜ 半導體
    """
    stock_id = str(stock_id).strip()
    url = GOODINFO_URL.format(stock_id=stock_id)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            html = response.text

            # 🔍 從 HTML 擷取產業分類 ➜ <td class="...">產業別</td><td>半導體</td>
            match = re.search(r"產業別.*?<td.*?>(.*?)</td>", html, re.DOTALL)
            if match:
                industry = match.group(1).strip()
                logger.info(f"🏷️ Goodinfo 查產業成功 ➜ {stock_id} ➜ {industry}")
                return industry
            else:
                logger.warning(f"⚠️ Goodinfo 無法解析產業 ➜ stock_id={stock_id}")
                return "未分類"
    except Exception as e:
        logger.exception(f"❌ Goodinfo 查產業失敗 ➜ {str(e)}")
        return "未分類"
