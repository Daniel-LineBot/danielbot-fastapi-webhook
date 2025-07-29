from routers.ai_finmind_v1 import get_finmind_dividend
from utils.stock_parser import extract_stock_id, normalize_query_type

def get_dividend_reply(query_text: str) -> str:
    stock_id = extract_stock_id(query_text)
    query_type = normalize_query_type(query_text)

    if not stock_id:
        return "❗ 無法辨識股票代碼，請再確認輸入內容。"

    try:
        data = get_finmind_dividend(stock_id)
        if not data:
            return f"查無 {stock_id} 的配息資料。可能尚未公布或來源缺漏。"

        reply = []
        for entry in data:
            year = entry.get("year")
            cash = entry.get("cash_dividend", 0)
            stock = entry.get("stock_dividend", 0)
            reply.append(f"{year} 年：現金股利 {cash} 元，股票股利 {stock} 股")

        return "\n".join(reply)

    except Exception as e:
        # Optional: fallback to TWSE or Goodinfo
        return f"查詢過程發生錯誤：{e}"

