import requests
from linebot.models import FlexSendMessage, MessageEvent, TextMessage
import logging

logger = logging.getLogger("uvicorn")



def bind_handler(handler):  # ✅ 接收從外部傳進來的 WebhookHandler 實例
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        text = event.message.text.strip()
        logger.info(f"✅ LINE callback 觸發 ➜ 訊息：{text}")
        if text.startswith("查詢"):
            query = text.replace("查詢", "").strip()
            stock_id = query if query.isdigit() else name_to_id(query)

            url = f"https://danielbot-fastapi-webhook-437280480144.asia-east1.run.app/ai-stock/price/{stock_id}"
            response = requests.get(url).json()

            bubble = reply_bubble_builder(response)
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=f"{stock_id} 查價結果", contents=bubble)
            )

