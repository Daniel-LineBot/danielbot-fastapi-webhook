from loguru import logger
from routers.twse import get_twse_name
from routers.goodinfo import get_goodinfo_name
from routers.mock_stock import get_mock_name

def get_stock_name_with_source(stock_id: str, source: str = "twse") -> dict:
    """
    查詢股票名稱並回傳 dict 結構：{ name, source, found }
    """
    stock_id = str(stock_id).strip()
    source = source.lower()
    name = "查無"

    if not stock_id:
        return {"name": name, "source": source, "found": False}

    if source == "twse":
        name = get_twse_name(stock_id)
    elif source == "goodinfo":
        name = get_goodinfo_name(stock_id)
    elif source == "mock":
        name = get_mock_name(stock_id)

    found = name and name != "查無"
    return {"name": name, "source": source, "found": found}

# 🔄 reverse 查詢 ➜ 名稱找代碼（模糊）
def reverse_name_lookup(name: str, source: str = "twse") -> str:
    """
    根據名稱模糊比對查代碼（只回傳第一筆）
    """
    from routers.twse import twse_stock_table  # twse_stock_table: Dict[str, str] ➜ {"2330": "台積電"}
    from routers.goodinfo import goodinfo_stock_table
    from routers.mock_stock import mock_stock_table

    name = name.strip()
    source = source.lower()

    if not name:
        return "查無"

    if source == "twse":
        table = twse_stock_table
    elif source == "goodinfo":
        table = goodinfo_stock_table
    elif source == "mock":
        table = mock_stock_table
    else:
        table = {}

    for sid, cname in table.items():
        if name in cname:
            return sid

    return "查無"

def get_stock_name(stock_id: str, source: str = "twse") -> str:
    """
    查詢股票名稱 ➜ 可選來源：twse, goodinfo, mock
    stock_id: 股票代碼（例如 "2330"）
    source: 資料來源（預設 twse）
    return: 股票名稱（例如 "台積電"）或 "查無"
    """
    logger.info(f"🔍 get_stock_name ➜ stock_id={stock_id}, source={source}")

    stock_id = str(stock_id).strip()

    if not stock_id:
        return "查無"

    source = source.lower()
    if source == "twse":
        return get_twse_name(stock_id)
    elif source == "goodinfo":
        return get_goodinfo_name(stock_id)
    elif source == "mock":
        return get_mock_name(stock_id)
    else:
        logger.warning(f"⚠️ 未知來源 ➜ {source}")
        return "查無"

