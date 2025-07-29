# modules/dividend_reply.py
from routers.ai_finmind_v1 import get_finmind_dividend
from utils.stock_parser import extract_stock_id, normalize_query_type

from services.twse_client import get_twse_dividend
from services.tdcc_client import get_cdib_dividend
from services.finmind_client import get_finmind_dividend
from loguru import logger

async def get_dividend_info(stock_id: str) -> dict:
    for source, fetcher in [
        ("TWSE", get_twse_dividend),
        ("集保", get_cdib_dividend),
        ("FinMind", get_finmind_dividend)
    ]:
        try:
            data = await fetcher(stock_id)
            if data and isinstance(data, dict) and len(data.keys()) > 1:
                data["source"] = source
                return data
        except Exception as e:
            logger.warning(f"[Fallback] {source} 讀取失敗：{e}")
    return {"error": "全部來源都查不到配息資料", "stock_id": stock_id}



def get_dividend_reply(query_text: str) -> str:
    stock_id = extract_stock_id(query_text)
    query_type = normalize_query_type(query_text)

    if not stock_id:
        return "❗ 無法辨識股票代碼，請再確認輸入內容。"

    try:
        data = get_finmind_dividend(stock_id)
        if not data:
            return f"查無 {stock_id} 的配息資料。可能尚未公布或來源缺漏。"

        # 💡 加在這裡最合適：
        logger.info(f"⛳ FinMind 查詢 stock_id={stock_id} dividend 中…")
        logger.info(f"📤 查詢結果：{data}")

        reply = []
        for entry in data:
            year = entry.get("year")
            cash = entry.get("cash_dividend", 0)
            stock = entry.get("stock_dividend", 0)
            reply.append(f"{year} 年：現金股利 {cash} 元，股票股利 {stock} 股")

        logger.info(f"📩 回覆訊息：{' | '.join(reply)}")  # ✅ 建議用 join 讓 log 更清楚
        return "\n".join(reply)


    except Exception as e:
        # Optional: fallback to TWSE or Goodinfo
        return f"查詢過程發生錯誤：{e}"

