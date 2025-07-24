# routers/cache.py ➜ 建立 metadata cache manager

from google.cloud import firestore
db = firestore.AsyncClient()

async def metadata_cache_manager(stock_id: str, metadata: dict):
    if not metadata or "收盤" not in metadata:
        return False  # 無有效資料不存入

    doc_ref = db.collection("ai_stock_metadata").document(stock_id)
    await doc_ref.set(metadata)
    return True
