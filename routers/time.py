__version__ = "2025.07.18"
from datetime import datetime, timezone, timedelta, time


def get_tw_time():
    """回傳台灣時區的 datetime.now()"""
    taiwan_tz = timezone(timedelta(hours=8))
    return datetime.now(taiwan_tz)

def get_tw_time_str(fmt="%Y%m%d"):
    """回傳指定格式的台灣時間字串"""
    return get_tw_time().strftime(fmt)

def get_tw_hour():
    """回傳台灣時間整點小時（int）"""
    return get_tw_time().hour

def is_open_twse():
    """判斷台股是否在盤中交易時間"""
    now_tw = get_tw_time().time()
    return time(9, 0) <= now_tw <= time(13, 30)

def get_tw_daypart():
    """回傳台灣時間目前屬於哪個交易段落：盤前 / 盤中 / 盤後 / 非交易日"""
    now = get_tw_time()
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    t = now.time()

    if weekday >= 5:  # 六日
        return "非交易日"
    elif t < time(9, 0):
        return "盤前"
    elif time(9, 0) <= t <= time(13, 30):
        return "盤中"
    else:
        return "盤後"
        
def is_market_open(market: str = "twse") -> bool:
    """判斷指定市場是否開盤中，目前支援 twse 台股"""
    now = get_tw_time().time()

    if market.lower() == "twse":
        start, end = twse_open_range()
        return start <= now <= end

    # 未支援市場 ➜ 預設為 False
    return False
    
def twse_open_range():
    """回傳台股交易時段起訖時間（time物件）"""
    return time(9, 0), time(13, 30)

def twse_status() -> dict:
    """台股交易狀態 ➜ 回傳 dict 包含 is_open, now, mode 字段"""
    now = get_tw_time()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    t = now.time()
    start, end = twse_open_range()

    is_open = start <= t <= end
    if now.weekday() >= 5:
        mode = "非交易日"
    elif t < start:
        mode = "盤前"
    elif is_open:
        mode = "盤中"
    else:
        mode = "盤後"

    return {
        "is_open": is_open,
        "now": now_str,
        "mode": mode
    }

# 動態產生 __all__（開發時使用 ➜ 可列印出 def 清單）
def get_all_exports():
    import inspect
    this_module = inspect.getmodule(inspect.currentframe())
    return [
        name for name, obj in vars(this_module).items()
        if inspect.isfunction(obj) and not name.startswith("_")
    ]

# ✅ 最終輸出 ➜ 你可以 print(get_all_exports()) 或直接複製結果
__all__ = [
    "get_tw_time",
    "get_tw_time_str",
    "get_tw_hour",
    "is_open_twse",
    "get_tw_daypart",
    "is_market_open",
    "twse_open_range",
    "twse_status",
    "fallback_trace"
]

