from loguru import logger
from routers.twse import get_twse_name
from routers.goodinfo import get_goodinfo_name
from routers.mock_stock import get_mock_name

from routers.stock import get_stock_info
from routers.twse import get_twse_industry
from routers.goodinfo import get_goodinfo_industry
from routers.mock_stock import get_mock_industry

async def get_stock_profile(text: str, source: str = "twse") -> dict:
    """
    一鍵查詢 ➜ 股票代碼、名稱、產業、目前成交價（用 callback 主幹查）
    """
    identity = get_stock_identity(text, source)
    stock_id = identity["id"]
    name = identity["name"]

    if stock_id == "查無":
        return {"id": "查無", "name": "查無", "industry": "查無", "price": "查無"}

    # 查產業分類
    if source == "twse":
        industry = get_twse_industry(stock_id)
    elif source == "goodinfo":
        industry = get_goodinfo_industry(stock_id)
    elif source == "mock":
        industry = get_mock_industry(stock_id)
    else:
        industry = "未知"

    # 查目前價格（fallback 啟用）
    result = await get_stock_info(stock_id)
    price = result.get("price", "查無")

    return {
        "id": stock_id,
        "name": name,
        "industry": industry,
        "price": price
    }
async def resolve_stock_input(text: str) -> dict:
    """
    智能解析使用者輸入 ➜ 自動選來源查詢
    優先順序：TWSE ➜ fallback Goodinfo ➜ mock
    """
    info = await get_stock_profile(text, source="twse")
    if info["price"] != "查無":
        info["source"] = "twse"
        return info

    # fallback ➜ goodinfo
    info = await get_stock_profile(text, source="goodinfo")
    if info["price"] != "查無":
        info["source"] = "goodinfo"
        return info

    # fallback ➜ mock
    info = await get_stock_profile(text, source="mock")
    info["source"] = "mock"
    return info

def get_stock_identity(text: str, source: str = "twse") -> dict:
    """
    自動判斷輸入是代碼還是名稱 ➜ 回傳 {id, name}
    """
    text = str(text).strip()
    source = source.lower()

    if not text:
        return {"id": "查無", "name": "查無"}

    if text.isdigit():
        stock_id = text
        name = get_stock_name(stock_id, source)
    else:
        stock_id = reverse_name_lookup(text, source)
        name = get_stock_name(stock_id, source)

    return {
        "id": stock_id if stock_id else "查無",
        "name": name if name else "查無"
    }

def get_stock_metadata(stock_id: str, source: str = "twse") -> dict:
    """
    回傳股票 metadata ➜ id, name, 產業（若支援）
    """
    from routers.twse import get_twse_industry
    from routers.goodinfo import get_goodinfo_industry
    from routers.mock_stock import get_mock_industry

    stock_id = str(stock_id).strip()
    source = source.lower()

    name = get_stock_name(stock_id, source)

    if source == "twse":
        industry = get_twse_industry(stock_id)
    elif source == "goodinfo":
        industry = get_goodinfo_industry(stock_id)
    elif source == "mock":
        industry = get_mock_industry(stock_id)
    else:
        industry = "未知"

    return {
        "id": stock_id,
        "name": name if name else "查無",
        "industry": industry if industry else "未分類"
    }

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

