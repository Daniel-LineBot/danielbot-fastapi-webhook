# routers/ai_stock_v1.py

from fastapi import APIRouter
from routers.twse import get_price_twse  # 引入 TWSE crawler

router = APIRouter()

@router.get("/ai-stock/ping")
async def ping():
    return {"status": "ai_stock_v1 ready"}

@router.get("/ai-stock/price/{stock_id}")
async def price_lookup(stock_id: str):
    result = await get_price_twse(stock_id)
    return result

