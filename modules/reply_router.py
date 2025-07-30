from modules.nlu import simple_nlu
from modules.dividend_fetcher import fetch_all_dividend
from modules.calendar import get_dividend_calendar

async def reply_router(user_text: str) -> dict:
    metadata = simple_nlu(user_text)
    intent = metadata.get("intent")
    stock_id = metadata.get("stock_id")
    year = metadata.get("year")

    if intent == "query_dividend" and stock_id:
        dividend_all = await fetch_all_dividend(stock_id, year)
        calendar = get_dividend_calendar(stock_id, year)
        reply = f"{stock_id} {year or ''}配息資訊\n"
        for d in dividend_all:
            reply += f"- {d['source']}: {d['data']}\n"
        reply += "行事曆：\n"
        for c in calendar:
            reply += f"- {c['event']}: {c['date']}\n"
        return {"text": reply}

    return {"text": "請輸入『股票代碼＋配息』查詢，例如：查2330今年配息"}
