def get_dividend_calendar(stock_id, year=None):
    # TODO：串配息日API，或自建事件
    # 回傳例：配息登記日、除息日、發放日
    return [
        {"event": "除息日", "date": "2025-08-15"},
        {"event": "發放日", "date": "2025-09-10"}
    ]