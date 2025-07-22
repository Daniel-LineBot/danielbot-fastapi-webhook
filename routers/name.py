import re
from loguru import logger

from routers.twse import get_twse_name
from routers.twse import get_twse_industry

from routers.goodinfo import get_goodinfo_name
from routers.goodinfo import get_goodinfo_industry

from routers.stock import get_stock_info

def get_stock_name(stock_id: str, source: str = "twse") -> str:

    logger.info(f"🔍 get_stock_name ➜ stock_id={stock_id}, source={source}")
    stock_id = str(stock_id).strip()

    if not stock_id:
        return "查無"

    source = source.lower()
    if source == "twse":
        return get_twse_name(stock_id)
    elif source == "goodinfo":
        return get_goodinfo_name(stock_id)
    else:
        logger.warning(f"⚠️ 未知來源 ➜ {source}")
        return "查無"

""" 
async def reply_stock_identity(text: str) -> str:
    """
    回覆股票身份語句 ➜ 台積電（2330） ➜ 半導體
    """
    info = await name_summary(text)
    return f"{info.get('name')}（{info.get('id')}） ➜ 產業分類：{info.get('industry')}"


async def reply_stock_label(text: str) -> str:
    """
    回覆股票名稱標籤 ➜ 台積電（2330）
    可用於 callback reply / logs / 前端提示語
    """
    info = get_stock_identity(text)
    return f"{info.get('name', '查無')}（{info.get('id', '查無')}）"

async def bubble_summary_flex(text: str) -> dict:
    """
    回傳完整 Flex Bubble ➜ 含 header 標題 / body 資料 / footer fallback 顯示
    """
    info = await resolve_stock_input(text, full=True)
    price_data = await get_stock_info(info["id"])
    name = info.get("name")
    stock_id = info.get("id")
    price = price_data.get("price", "查無")
    open_ = price_data.get("open", "查無")
    high = price_data.get("high", "查無")
    low = price_data.get("low", "查無")
    source = info.get("source", "未知")
    mode = info.get("fallback_mode", "未知")
    industry = info.get("industry", "未分類")

    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "text",
                "text": f"{name}（{stock_id}）",
                "weight": "bold",
                "size": "xl"
            }]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                { "type": "text", "text": f"成交價：{price} 元" },
                { "type": "text", "text": f"開盤：{open_} ➜ 高點：{high} ➜ 低點：{low}" },
                { "type": "text", "text": f"產業分類：{industry}" },
                { "type": "text", "text": f"時間：{price_data.get('datetime', '查無')}" }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                { "type": "text", "text": f"來源：{source.upper()} ➜ 模式：{mode}", "size": "xs", "color": "#AAAAAA" }
            ]
        }
    }

async def get_reply_and_payload(text: str) -> dict:
    """
    同時回語意 reply 字串 ＋ 查詢 payload 結構 dict
    用於 webhook 同步 reply 文字與回傳 JSON
    """
    info = await resolve_stock_input(text, full=True)
    price_data = await get_stock_info(info["id"])

    reply = compose_reply(info, price_data.get("price", "查無"))
    payload = {
        "id": info.get("id"),
        "name": info.get("name"),
        "industry": info.get("industry"),
        "price": price_data.get("price"),
        "open": price_data.get("open"),
        "high": price_data.get("high"),
        "low": price_data.get("low"),
        "datetime": price_data.get("datetime"),
        "source": info.get("source"),
        "fallback_mode": info.get("fallback_mode", "未標註")
    }

    return {
        "reply": reply,
        "payload": payload
    }

async def payload_trace(text: str) -> dict:
    """
    logs trace ➕ 回傳完整 payload 結構（callback webhook 用）
    """
    info = await resolve_stock_input(text, full=True)
    price_data = await get_stock_info(info["id"])

    payload = {
        "name": info.get("name"),
        "id": info.get("id"),
        "industry": info.get("industry"),
        "price": price_data.get("price"),
        "open": price_data.get("open"),
        "high": price_data.get("high"),
        "low": price_data.get("low"),
        "datetime": price_data.get("datetime"),
        "source": info.get("source"),
        "fallback_mode": info.get("fallback_mode", "未標註")
    }

    logger.info(f"[payload_trace] ➜ {payload}")
    return payload

async def bubble_summary_full(text: str) -> dict:
    """
    回傳完整行情 Flex Bubble JSON ➜ open, high, low, price, datetime, fallback_mode
    """
    info = await resolve_stock_input(text, full=True)
    price_data = await get_stock_info(info["id"])

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": f"{info['name']}（{info['id']}）", "weight": "bold", "size": "xl"},
                {"type": "text", "text": f"成交價：{price_data.get('price', '查無')} 元", "size": "sm"},
                {"type": "text", "text": f"開盤價：{price_data.get('open', '查無')} ➜ 高點：{price_data.get('high', '查無')} ➜ 低點：{price_data.get('low', '查無')}", "size": "sm"},
                {"type": "text", "text": f"時間：{price_data.get('datetime', '查無')}", "size": "xs", "color": "#999999"},
                {"type": "text", "text": f"產業分類：{info.get('industry', '查無')}", "size": "sm"},
                {"type": "text", "text": f"資料來源：{info.get('source', '未知').upper()} ➜ 模式：{info.get('fallback_mode', '未知')}", "size": "xs", "color": "#AAAAAA"}
            ]
        }
    }


async def price_and_industry(text: str) -> str:
    """
    回「台積電 ➜ 成交：854 元 ➜ 產業：半導體」
    用於精簡語意回覆 or Bubble 摘要
    """
    info = await resolve_stock_input(text, full=True)
    price = info.get("price", "查無")
    name = info.get("name", "查無")
    industry = info.get("industry", "未分類")
    return f"{name} ➜ 成交：{price} 元 ➜ 產業：{industry}"

async def bubble_summary(text: str) -> dict:
    """
    回傳一段 Flex Bubble 用的 JSON 結構 ➜ 名稱 / 成交價 / 產業 / fallback
    """
    info = await resolve_stock_input(text, full=True)
    price_data = await get_stock_info(info["id"])

    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://example.com/stock_banner.png",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"{info['name']}（{info['id']}）",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "text",
                    "text": f"成交價：{price_data.get('price', '查無')} 元",
                    "size": "sm",
                    "color": "#666666",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": f"產業分類：{info['industry']}",
                    "size": "sm",
                    "color": "#999999",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": f"來源：{info['source'].upper()} ➜ 模式：{info.get('fallback_mode', '未知')}",
                    "size": "xs",
                    "color": "#999999",
                    "wrap": True
                }
            ]
        }
    }

async def price_only_trace(text: str) -> str:
    """
    logs trace 成交價查詢 ➕ 回覆「目前價格為 X 元」
    用於 webhook 簡化查價場景
    """
    info = await resolve_stock_input(text, full=True)
    price = info.get("price", "查無")
    logger.info(f"[price_only_trace] {info.get('name')}（{info.get('id')}） ➜ 成交價 {price} 元 ➜ 來源：{info.get('source')}")
    return f"目前價格為 {price} 元"

async def get_kline_summary(text: str) -> str:
    """
    回傳語意行情摘要 ➜ 今日開盤 / 高點 / 成交價
    適用於 callback bubble 顯示 / logs trace 比對
    """
    info = await resolve_stock_input(text, full=True)
    price_data = await get_stock_info(info["id"])

    open_price = price_data.get("open", "查無")
    high_price = price_data.get("high", "查無")
    price = price_data.get("price", "查無")

    name = info.get("name", "查無")
    stock_id = info.get("id", "查無")

    return f"📊 {name}（{stock_id}）\n今日開盤：{open_price} ➜ 高點：{high_price} ➜ 成交：{price}"

async def quick_trace(text: str) -> str:
    """
    logs trace + 快速回覆語句 ➜ 回「成交價 858 元」
    適合 webhook callback 簡化處理 ➜ 回應與 trace 同步
    """
    info = await resolve_stock_input(text, full=True)
    price = info.get("price", "查無")
    name_stock_trace(info, price)
    logger.info(f"[QuickTrace] ➜ 查詢 {info.get('name')}（{info.get('id')}） ➜ 成交價 {price} 元 ➜ 來源：{info.get('source')}")
    return f"成交價 {price} 元"
async def stock_payload_verbose(text: str) -> dict:
    """
    查詢股票完整 payload（進階版） ➜ price, open, high, low, name, id, source_detail
    適合前端顯示 K 線摘要或語意 bubble
    """
    info = await resolve_stock_input(text, full=True)
    stock_id = info.get("id", "查無")

    # 查主幹行情 ➜ 必須從 stock.py 查 info 結構
    raw = await get_stock_info(stock_id)
    return {
        "id": info.get("id"),
        "name": info.get("name"),
        "industry": info.get("industry"),
        "source": info.get("source"),
        "fallback_mode": info.get("fallback_mode", "未標註"),
        "price": raw.get("price"),
        "open": raw.get("open"),
        "high": raw.get("high"),
        "low": raw.get("low"),
        "datetime": raw.get("datetime"),
        "source_detail": raw.get("source")  # 可能是 TWSE / Goodinfo
    }

async def reply_stock_price_only(text: str) -> str:
    """
    快速回覆語句 ➜ 只回成交價：「成交價 858 元」
    適合 LINE Quick Reply / bubble 中使用
    """
    info = await resolve_stock_input(text)
    price = info.get("price", "查無")
    return f"成交價 {price} 元"

async def stock_payload(text: str) -> dict:
    """
    查詢股票完整 payload ➜ 給前端用 ➜ name, id, price, source
    """
    info = await resolve_stock_input(text, full=True)
    return {
        "name": info.get("name"),
        "id": info.get("id"),
        "price": info.get("price"),
        "source": info.get("source"),
        "industry": info.get("industry")
    }
async def stock_query_summary(text: str) -> dict:
    """
    一行取得 `{id, name, price, source, fallback_mode}` ➜ callback reply 可直接吃
    """
    info = await resolve_stock_input(text, full=True)

    return {
        "id": info.get("id", "查無"),
        "name": info.get("name", "查無"),
        "price": info.get("price", "查無"),
        "source": info.get("source", "查無"),
        "fallback_mode": info.get("fallback_mode", "查無")
    }

async def resolve_stock_source_chain(text: str) -> str:
    """
    回傳查詢流程語句 ➜ 例如：
    「來源：TWSE ➜ fallback Goodinfo ➜ 查無」
    """
    trace = ["TWSE"]
    info = await get_stock_profile(text, source="twse")
    if info.get("price") != "查無":
        return f"來源：TWSE ➜ 成功"

    trace.append("fallback Goodinfo")
    info = await get_stock_profile(text, source="goodinfo")
    if info.get("price") != "查無":
        return f"來源：TWSE ➜ fallback Goodinfo ➜ 成功"

    trace.append("查無")
    return " ➜ ".join(["來源"] + trace)

async def name_summary(text: str, source: str = "twse") -> dict:
    """
    只回傳名稱 / 代碼 / 產業分類 ➜ 不查價格
    """
    info = get_stock_identity(text, source)
    stock_id = info["id"]
    name = info["name"]

    if stock_id == "查無":
        return {"id": "查無", "name": "查無", "industry": "查無"}

    # ✅ 只允許 twse 和 goodinfo ➜ fallback 成功率最高
    source = source.lower()
    if source == "twse":
        industry = get_twse_industry(stock_id)
    elif source == "goodinfo":
        industry = get_goodinfo_industry(stock_id)
    else:
        # ✅ fallback 來源失敗 ➜ 自動用 TWSE 查分類
        industry = get_twse_industry(stock_id)

    return {
        "id": stock_id,
        "name": name,
        "industry": industry
    }


async def hint_trace(text: str) -> str:
    """
    logs trace + 語意回覆同步執行 ➜ 一次輸入即顯示
    """
    info = await resolve_stock_input(text, full=True)
    price = info.get("price", "查無")
    name_stock_trace(info, price)
    logger.info(f"[查詢摘要] ➜ {query_summary(info)}")
    return compose_reply(info, price)

def query_summary(info: dict) -> dict:
    """
    將 info 結構整理為 summary dict ➜ logs 顯示完整資訊
    """
    return {
        "stock_id": info.get("id"),
        "stock_name": info.get("name"),
        "industry": info.get("industry"),
        "price": info.get("price"),
        "source": info.get("source"),
        "fallback_mode": info.get("fallback_mode", "未標註")
    }

async def callback_router(text: str) -> str:
    """
    根據查價結果動態回覆語意語句 ➜ 若查無則回傳提示語
    """
    info = await resolve_stock_input(text, full=True)
    price = info.get("price", "查無")

    if price == "查無":
        return f"⚠️ 查詢失敗 ➜ 無法取得 {info.get('name')}（{info.get('id')}） 的成交價"
    
    name_stock_trace(info, price)
    return compose_reply(info, price)

async def get_stock_reply(text: str) -> str:
    """
    一行 callback 用法 ➜ 回傳完整語句含名稱、成交價、產業、來源
    """
    info = await resolve_stock_input(text, full=True)
    price = info.get("price", "查無")
    name_stock_trace(info, price)
    return compose_reply(info, price)
    
async def hint_reply(text: str) -> str:
    """
    回傳推薦語意語句 ➜ 加 emoji 與 fallback 判斷提示
    """
    info = await resolve_stock_input(text, full=True)
    price = info.get("price", "查無")
    mode = info.get("fallback_mode", "未知模式")
    name = info.get("name", "查無")
    stock_id = info.get("id", "查無")

    return f"📢 查詢 {name}（{stock_id}） ➜ 成交價 {price} 元\n🔍 判斷模式：{mode}"

async def resolve_stock_input(text: str, full: bool = False) -> dict:
    """
    智能解析 ➜ 自動 fallback 路徑選擇
    若 full=True ➜ 回傳 fallback path 與 TWSE 判斷
    """
    info = await get_stock_profile(text, source="twse")
    if info.get("price") != "查無":
        info["source"] = "twse"
        if full:
            info["fallback_mode"] = "即時查詢"
        return info

    info = await get_stock_profile(text, source="goodinfo")
    if info.get("price") != "查無":
        info["source"] = "goodinfo"
        if full:
            info["fallback_mode"] = "歷史查詢 ➜ TWSE 失敗 ➜ fallback Goodinfo"
        return info

    # 🧹 全部來源都查無 ➜ 回傳空值結構
    return {
        "id": "查無",
        "name": "查無",
        "price": "查無",
        "industry": "查無",
        "source": "查無",
        "fallback_mode": "無有效來源"
    }


async def get_stock_hint(text: str, source: str = "auto") -> str:
    """
    產出語意語句：「查詢台積電（2330） ➜ 成交價 858 元」
    source="auto" ➜ 自動 fallback（TWSE ➜ Goodinfo ➜ Mock）
    """
    if source == "auto":
        info = await resolve_stock_input(text)
    else:
        info = await get_stock_profile(text, source)

    price = info.get("price", "查無")
    return compose_reply(info, price)

def name_stock_trace(info: dict, price: Union[str, int]):
    """
    logs trace 用 ➜ 回報名稱、代碼、產業、價格、來源
    """
    logger.info(f"[name_stock_trace] 名稱={info.get('name')} ➜ 代碼={info.get('id')} ➜ 價格={price} ➜ 來源={info.get('source')}")

def compose_reply(info: dict, price: Union[str, int]) -> str:
    """
    組合 callback reply 語句 ➜ 台積電（2330）成交價 858 元
    info: 包含 name, id, industry, source 等欄位
    price: 成交價
    """
    name = info.get("name", "查無")
    stock_id = info.get("id", "查無")
    industry = info.get("industry", "未分類")
    source = info.get("source", "未知").upper()

    return f"📈 {name}（{stock_id}）\n成交價：{price} 元\n產業分類：{industry}\n資料來源：{source}"

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
    stock_id = str(stock_id).strip()
    source = source.lower()

    name = get_stock_name(stock_id, source)

    if source == "twse":
        industry = get_twse_industry(stock_id)
    elif source == "goodinfo":
        industry = get_goodinfo_industry(stock_id)
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

    found = name and name != "查無"
    return {"name": name, "source": source, "found": found}

# 🔄 reverse 查詢 ➜ 名稱找代碼（模糊）
def reverse_name_lookup(name: str, source: str = "twse") -> str:
    """
    根據名稱模糊比對查代碼（只回傳第一筆）
    """
    name = name.strip()
    source = source.lower()

    if not name:
        return "查無"

    if source == "twse":
        table = twse_stock_table
    elif source == "goodinfo":
        table = goodinfo_stock_table
    else:
        table = {}

    for sid, cname in table.items():
        if name in cname:
            return sid

    return "查無"
"""


