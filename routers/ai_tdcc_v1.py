# routers/ai_tdcc_v1.py

from fastapi import APIRouter
import requests

router = APIRouter()

TDCC_ENDPOINT = "https://www.tdcc.com.tw/smWeb/QryStockAjax.do"  # 集保查詢 POST 端點
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": "https://www.tdcc.com.tw/smWeb/QryStock.jsp",
}

@router.get("/tdcc/{stock_id}")
def get_tdcc_data(stock_id: str):
    payload = {
        "encodeStockId": stock_id,
        "isnew": "true"
    }

    try:
        response = requests.post(TDCC_ENDPOINT, headers=HEADERS, data=payload)
        response.raise_for_status()
        tdcc_data = response.json()
        return {
            "status": "success",
            "
