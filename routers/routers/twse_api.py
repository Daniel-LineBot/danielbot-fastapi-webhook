# routers/twse_api.py
import httpx
import logging
from datetime import datetime
logger = logging.getLogger("uvicorn")

async def get_price_twse_json(stock_id: str) -> dict:
    url = f"https://www.twse.com.tw/rwd/zh/stock?format=json&stockNo={stock_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            logger.warning(f"❌ TWSE API metadata fail ➜ status: {resp.status_code}")
            return {"stock_id": stock_id, "price": "--", "change": "--", "timestamp": "--", "source": "TWSE_API"}

        data = resp.json()
        rows = data.get("data", [])
        if not rows or not isinstance(rows, list) or not rows[0]:
            logger.warning(f"❌ TWSE API metadata empty ➜ stock_id: {stock_id}")
            return {"stock_id": stock_id, "price": "--", "change": "--", "timestamp": "--", "source": "TWSE_API"}

        row = rows[0]
        price = row[2] if len(row) >= 3 else "--"
        change = row[4] if len(row) >= 5 else "--"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"✅ TWSE API crawler success ➜ stock_id: {stock_id} ➜ price: {price} ➜ change: {change}")
        return {
            "stock_id": stock_id,
            "price": price,
            "change": change,
            "timestamp": timestamp,
            "source": "TWSE_API"
        }
