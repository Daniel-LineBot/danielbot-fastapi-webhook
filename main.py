from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = FastAPI()

from routers import webhook
app.include_router(webhook.router)


# LINE Bot 憑證
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
if not LINE_SECRET or not LINE_TOKEN:
    raise RuntimeError("請先設定環境變數 LINE_CHANNEL_SECRET、LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)

# --- 1) LINE Webhook endpoint ---
@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("x-line-signature", "")
    body = (await request.body()).decode("utf-8")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_text = event.message.text.strip()
    reply = f"你好，我是 DanielBot ??\n你剛才說的是：「{user_text}」"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))


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
