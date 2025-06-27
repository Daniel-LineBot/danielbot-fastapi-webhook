from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = FastAPI()

# LINE Bot ����
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
if not LINE_SECRET or not LINE_TOKEN:
    raise RuntimeError("�Х��]�w�����ܼ� LINE_CHANNEL_SECRET�BLINE_CHANNEL_ACCESS_TOKEN")

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
    reply = f"�A�n�A�ڬO DanielBot ??\n�A��~�����O�G�u{user_text}�v"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))


# --- 2) Copilot alert endpoint ---
class AlertPayload(BaseModel):
    type: str
    title: str
    message: str

@app.post("/copilot-alert")
async def copilot_alert(payload: AlertPayload):
    """
    Copilot �I�s�����ѡA�����t��ĵ��
    �d�� body:
    {
      "type": "billing_alert",
      "title": "Cloud Run �W�X�K�O�B��",
      "message": "?? ����w�ϥ� 100% �K�O�B�סA���ˬd�A�Ȫ��A�C"
    }
    """
    # TODO: broadcast or push to specific user(s)
    # �U���ܽd�L�X�A�]�i��� line_bot_api.broadcast(...)
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
    Copilot �ǤJ user text�A�^�ǷN�ϵ��c�Ƶ��G
    �d�� body:
    {
      "text": "���ڬd�@�U 2330 ����ѻ�"
    }
    �^��:
    {
      "intent": "query_stock_price",
      "confidence": 0.98
    }
    """
    # TODO: ���W�u���� NLU �ҫ�
    # �o�̥ܽd�^�� stub
    return NLUResponse(intent="unknown", confidence=0.0)
