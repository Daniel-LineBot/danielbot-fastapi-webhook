# modules/reply_router.py

from routers.ai_stock_v2 import get_stock_info, get_dividend_info

async def reply_router(metadata: dict) -> str:
    stock_id = metadata.get("stock_id")
    query_type = metadata.get("query_type")
    date = metadata.get("date")

    if not stock_id or not query_type:
        return (
            f"你剛說的是：{metadata['raw']}\n\n"
            "💡 指令範例：\n查詢 2330\n查詢 2330 20250701\n配息 2330"
        )

    try:
        if query_type == "dividend":
            info = await get_dividend_info(stock_id)
            return (
                f"💰 {stock_id} 配息資訊\n"
                f"年度：{info.get('year', '-')}\n"
                f"現金股利：{info.get('cash_dividend', '-')}\n"
                f"股票股利：{info.get('stock_dividend', '-')}\n"
                f"除權息日：{info.get('ex_dividend_date', '-')}\n"
                f"來源：{info.get('source', '-')}"
            )
        else:
            info = await get_stock_info(stock_id, date)
            return (
                f"📈 {info.get('name', '')}（{stock_id}）\n"
                f"成交價：{info.get('price', '-')}\n"
                f"開盤：{info.get('open', '-')}\n"
                f"最高：{info.get('high', '-')}\n"
                f"最低：{info.get('low', '-')}\n"
                f"成交量：{info.get('volume', '-')}\n"
                f"查詢日期：{info.get('date', '-')}\n"
                f"來源：{info.get('source', '-')}"
            )
    except Exception as e:
        logger.exception(f"🛑 callback 錯誤：{e}")
        return f"⚠️ 查詢失敗：{str(e)}"

