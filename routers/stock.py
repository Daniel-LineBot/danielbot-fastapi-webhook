from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/stock/{stock_id}")
async def get_stock_info(stock_id: str):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    if not data["msgArray"]:
        return {"error": "找不到股票代號，請確認輸入正確"}

    info = data["msgArray"][0]
    
    result = {
        "股票名稱": info["n"],
        "股票代號": info["c"],
        "成交價": info["z"],
        "漲跌": info["y"],
        "昨收": info["y"],
        "開盤": info["o"],
        "產業別": info.get("ind", "N/A")
    }

    return result
