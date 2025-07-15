from typing import Optional, Union
from datetime import datetime

def is_twse_open():
    now_hour = int(datetime.now().strftime("%H"))
    return 9 <= now_hour <= 13

async def get_stock_info(stock_id: str, date: Optional[Union[str, None]] = None):
    # 模擬錯誤代號情境
    if stock_id not in ["2330", "2317"]:
        return {"error": f"查無此代號：{stock_id}"}

    # 模擬日期錯誤格式
    if date and not str(date).isdigit():
        return {"error": f"日期格式錯誤 ➜ {date}"}

    # 模擬 fallback 模式
    if not date:
        return {
            "資料來源": "即時查詢",
            "股票名稱": "台積電",
            "股票代號": stock_id,
            "成交價": "850.00",
            "昨收": "848.00",
            "開盤": "851.00",
            "產業別": "半導體"
        }

    # 模擬歷史查詢
    if date == "20250701":
        return {
            "資料來源": "歷史盤後",
            "股票代號": stock_id,
            "股票名稱": "台積電",
            "原始查詢日期": date,
            "實際回傳日期": date,
            "開盤": "842.00",
            "最高": "855.00",
            "最低": "841.00",
            "收盤": "850.00",
            "成交量(張)": "123456",
            "提示": "此為模擬資料，非真實成交紀錄"
        }

    return {"error": f"查詢日期 {date} 無資料"}
