from loguru import logger
from routers.twse import get_twse_name
from routers.goodinfo import get_goodinfo_name
from routers.mock_stock import get_mock_name

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

