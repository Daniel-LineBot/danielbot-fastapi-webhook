# routers/formatter.py

def ai_stock_response_formatter(raw: dict) -> dict:
    if "error" in raw:
        return {
            "錯誤訊息": raw.get("error"),
            "fallback階層": raw.get("fallback階層", "未知"),
            "提示": raw.get("提示", "請稍後再試")
        }

    return {
        "股票代號": raw.get("股票代號", "未知"),
        "股票名稱": raw.get("股票名稱", "未知"),
        "收盤": raw.get("收盤", "N/A"),
        "漲跌": raw.get("漲跌", "N/A"),
        "開盤": raw.get("開盤", "N/A"),
        "成交量": raw.get("成交量", "N/A"),
        "資料時間": raw.get("資料時間", "未知"),
        "資料來源": raw.get("來源", "未知"),
        "fallback階層": raw.get("fallback階層", "未知")
    }
def ai_stock_response_formatter_enhanced(raw: dict) -> dict:
    if "error" in raw:
        return {
            "錯誤訊息": raw.get("error"),
            "fallback階層": raw.get("fallback階層", "未知"),
            "提示": raw.get("提示", "請稍後再試")
        }

    return {
        "股票代號": raw.get("股票代號", "未知"),
        "股票名稱": raw.get("股票名稱", "未知"),
        "收盤": raw.get("收盤", "N/A"),
        "漲跌": raw.get("漲跌", "N/A"),
        "開盤": raw.get("開盤", "N/A"),
        "成交量": raw.get("成交量", "N/A"),
        "資料時間": raw.get("資料時間", "未知"),
        "資料來源": raw.get("來源", "未知"),
        "fallback階層": raw.get("fallback階層", "未知"),
        "EPS": raw.get("EPS", "N/A"),
        "本益比": raw.get("本益比", "N/A"),
        "產業別": raw.get("產業別", "N/A")
    }
