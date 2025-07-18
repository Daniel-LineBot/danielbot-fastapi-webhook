from datetime import datetime, timezone, timedelta

def get_tw_time():
    """回傳台灣時區的 datetime.now()"""
    taiwan_tz = timezone(timedelta(hours=8))
    return datetime.now(taiwan_tz)

def get_tw_time_str(fmt="%Y%m%d"):
    """回傳指定格式的台灣時間字串"""
    return get_tw_time().strftime(fmt)

def get_tw_hour():
    """回傳台灣時區整點小時（int）"""
    return get_tw_time().hour
