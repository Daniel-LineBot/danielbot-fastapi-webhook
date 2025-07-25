import re
from datetime import datetime

def extract_stock_query(text: str) -> dict:
    query = {"stock_id": None, "date": None}
    if not text or not isinstance(text, str):
        return query

    try:
        clean_text = re.sub(r"(查詢|查|股價|看看|請問|一下|幫我)", "", text, flags=re.IGNORECASE).strip()
        parts = clean_text.split()

        for part in parts:
            if re.match(r"^\d{4}$", part):  # 股票代碼
                query["stock_id"] = part
            elif re.match(r"^\d{8}$", part):  # 日期格式 20250725
                try:
                    query["date"] = datetime.strptime(part, "%Y%m%d").date().isoformat()
                except ValueError:
                    pass

        # 沒有填日期 ➜ 預設今天
        if not query["date"]:
            query["date"] = datetime.now().date().isoformat()

        return query

    except Exception as e:
        print(f"❌ extract_stock_query 出錯：{e}")
        return query
