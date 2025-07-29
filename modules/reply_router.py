def reply_router(metadata: dict) -> str:
    qtype = metadata.get("query_type")
    stock_id = metadata.get("stock_id")

    if not stock_id:
        return "❗ 無法辨識股票代碼，請再確認輸入內容。"

    if qtype == "dividend":
        return get_dividend_reply(metadata["raw"])
    elif qtype == "price":
        return get_stock_price_reply(metadata["raw"])
    else:
        return "❓ 查詢意圖不明，請輸入『2330 配息』或『2303 股價』"
