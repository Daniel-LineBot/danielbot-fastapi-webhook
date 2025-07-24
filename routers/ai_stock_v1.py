# routers/ai_stock_v1.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/ai-stock/ping")
async def ping():
    return {"status": "ai_stock_v1 ready"}

