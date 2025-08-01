from modules.nlu import simple_nlu
from modules.dividend_fetcher import fetch_all_dividend
from formatter_twse import format_dividend as twse_formatter
from formatter_finmind import format_dividend as finmind_formatter
from formatter_tdcc import format_dividend as tdcc_formatter

def get_formatter(source: str):
    return {
        "TWSE": twse_formatter,
        "FinMind": finmind_formatter,
        "TDCC": tdcc_formatter
    }.get(source, lambda x: f"[⚠️ 無 formatter] {source}")

async def reply_router(user_text: str) -> dict:
    print(f"[DEBUG] user_text={user_text}")
    metadata = simple_nlu(user_text)
    print(f"[DEBUG] NLU metadata={metadata}")
    intent = metadata.get("intent")
    stock_id = metadata.get("stock_id")
    year = metadata.get("year")

    if intent == "query_dividend" and stock_id:
        dividend_all = await fetch_all_dividend(stock_id, year)
        reply = f"{stock_id} {year or ''}配息資訊\n"

        for d in dividend_all:
            formatter = get_formatter(d["source"])
            reply += formatter(d["data"]) + "\n"

        print(f"[DEBUG] reply={reply}")
        return {"text": reply}

    return {
        "text": f"[DEBUG] 未解析到配息查詢，user_text={user_text}, intent={intent}, stock_id={stock_id}"
    }
