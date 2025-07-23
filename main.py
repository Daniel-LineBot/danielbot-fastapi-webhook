# [DanielBot] Clean fallback commit @ 2025-07-23 16:31
# main.py 只需初始化 FastAPI 與掛載 router，不定義 webhook handler
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

from routers import webhook
#from routers import stock

app = FastAPI()
app.include_router(webhook.router)
#app.include_router(stock.router)

print("✅ DanielBot webhook app 啟動中… FastAPI 已掛上 /webhook")
print("📚 所有已掛載的路由：", app.routes)

# LINE Bot 憑證
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
if not LINE_SECRET or not LINE_TOKEN:
    raise RuntimeError("請先設定環境變數 LINE_CHANNEL_SECRET、LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_TOKEN)  # 用來 broadcast 或 push
handler = WebhookHandler(LINE_SECRET)  # webhook.py 引入同一實例


# --- 2) Copilot alert endpoint ---
class AlertPayload(BaseModel):
    type: str
    title: str
    message: str

@app.post("/copilot-alert")
async def copilot_alert(payload: AlertPayload):
    """
    Copilot 呼叫此路由，推播系統警示
    範例 body:
    {
      "type": "billing_alert",
      "title": "Cloud Run 超出免費額度",
      "message": "?? 本月已使用 100% 免費額度，請檢查服務狀態。"
    }
    """
    # TODO: broadcast or push to specific user(s)
    # 下面示範印出，也可改用 line_bot_api.broadcast(...)
    print(f"[COPILOT ALERT] {payload.type} - {payload.title}: {payload.message}")
    return {"status": "alert received"}


# --- 3) Copilot NLU endpoint ---
class NLURequest(BaseModel):
    text: str

class NLUResponse(BaseModel):
    intent: str
    confidence: float

@app.post("/copilot-nlu", response_model=NLUResponse)
async def copilot_nlu(req: NLURequest):
    """
    Copilot 傳入 user text，回傳意圖結構化結果
    範例 body:
    {
      "text": "幫我查一下 2330 今日股價"
    }
    回傳:
    {
      "intent": "query_stock_price",
      "confidence": 0.98
    }
    """
    # TODO: 接上真正的 NLU 模型
    # 這裡示範回傳 stub
    return NLUResponse(intent="unknown", confidence=0.0)
    
print("✅ DanielBot webhook app 啟動中… FastAPI 已掛上 /webhook")
print("📚 所有已掛載的路由：", app.routes)

