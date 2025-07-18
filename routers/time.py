from datetime import datetime, timezone, timedelta

def get_tw_time():
    """回傳台灣時區的 datetime.now()"""
    taiwan_tz = timezone(timedelta(hours=8))
    return datetime.now(taiwan_tz)
