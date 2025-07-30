import re

def simple_nlu(text: str) -> dict:
    """
    解析查詢意圖、股票代碼、年份，支援多種文字格式
    """
    intent = None
    stock_id = None
    year = None

    # 股票代碼四碼
    m_stock = re.search(r'(\d{4})', text)
    if m_stock:
        stock_id = m_stock.group(1)
    # 年份
    m_year = re.search(r'(\d{4})年', text)
    if m_year:
        year = int(m_year.group(1))
    if "配息" in text or "股利" in text:
        intent = "query_dividend"

    return {
        "intent": intent,
        "stock_id": stock_id,
        "year": year
    }