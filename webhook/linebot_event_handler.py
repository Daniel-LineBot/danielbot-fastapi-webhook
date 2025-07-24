import requests
from linebot.models import FlexSendMessage, MessageEvent, TextMessage
import logging
logger = logging.getLogger("uvicorn")
BASE_URL = "https://danielbot-fastapi-webhook-437280480144.asia-east1.run.app"  # ✅ Cloud Run 的 webhook URL




def bind_handler(handler):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        text = event.message.text.strip()
        logger.info(f"✅ LINE callback 觸發 ➜ 訊息：{text}")  # ✅ callback trace

        if text.startswith("查詢"):
            query = text.replace("查詢", "").strip()
            stock_id = query if query.isdigit() else name_to_id(query)

            if not stock_id:
                logger.warning(f"❌ 查詢失敗 ➜ 查無股票代號：{query}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"查無股票代號「{query}」，請輸入正確台股代碼")
                )
                return

            url = f"{BASE_URL}/ai-stock/price/{stock_id}"
            response = requests.get(url).json()
            bubble = reply_bubble_builder(response)
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=f"{stock_id} 查價結果", contents=bubble)
            )
            logger.info(f"✅ reply 查價完成 ➜ 回覆股票代號 {stock_id}")  # ✅ reply trace


