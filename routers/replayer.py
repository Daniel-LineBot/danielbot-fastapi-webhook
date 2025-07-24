# routers/replayer.py ➜ fallback trace replay builder

from google.cloud import firestore

async def router_fallback_result_replayer(stock_id: str) -> dict:
    doc_ref = firestore.AsyncClient().collection("ai_stock_metadata").document(stock_id)
    snapshot = await doc_ref.get()

    if not snapshot.exists:
        return {
            "錯誤": f"{stock_id} 尚無快取資料",
            "提示": "請先查詢一次以建立 fallback trace"
        }

    data = snapshot.to_dict()
    data["replay模式"] = "TRUE"
    return ai_stock_response_formatter_enhanced(data)
