import requests
import logging
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from webhook.stock_utils import name_to_id
from webhook.log_trace_decorator import log_trace

logger = logging.getLogger("uvicorn")
BASE_URL = "https://danielbot-fastapi-webhook-437280480144.asia-east1.run.app"

def bind_handler(handler: WebhookHandler) -> WebhookHandler:
    @handler.add(MessageEvent, message=TextMessage)
    @log_trace("LINE Callback Handler")
    async def handle_message(event):
        text = event.message.text.strip()
        logger.info(f"✅ LINE callback 觸發 ➜ 訊息：{text}")

        if not text.startswith("查詢"):
            return  # 不是查詢指令就跳出

        query = text.replace("查詢", "").strip()
        stock_id = query if query.isdigit() else name_to_id(query)

        if not stock_id:
            await line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"查無股票代號「{query}」，請輸入正確台股代碼")
            )
            logger.warning(f"❌ 查詢失敗 ➜ 查無股票代號：{query}")
            return

        url = f"{BASE_URL}/ai-stock/price/{stock_id}"
        resp = requests.get(url)

        if resp.status_code != 200:
            await line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"查價失敗 ➜ 無法取得「{stock_id}」資料，請稍後再試")
            )
            logger.warning(f"❌ 查價 API 回應異常 ➜ status: {resp.status_code}")
            return

        response = resp.json()
        reply_text = (
            f"📈 {stock_id} 查價結果\n"
            f"💵 成交價：{response.get('price', '--')}\n"
            f"📊 漲跌：{response.get('change', '--')}\n"
            f"🕒 時間：{response.get('timestamp', '--')}"
        )

        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        logger.info(f"✅ reply 查價完成 ➜ 回覆股票代號 {stock_id}")

    return handler  # ✅ 確保這行是 bind_handler 的正確 return，不被 async 包住

"""
def bind_handler(handler):
    @handler.add(MessageEvent, message=TextMessage)
    @log_trace("LINE Callback Handler")
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
            resp = requests.get(url)
            
            if resp.status_code != 200 or not resp.text.strip():
                logger.warning(f"❌ 查價 API 回應異常 ➜ status: {resp.status_code} ➜ body: {resp.text}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"查價失敗 ➔ 無法取得「{stock_id}」資料，請稍後再試")
                )
                return
            
            response = resp.json()
            bubble = reply_bubble_builder(response)
            
            logger.info(f"📦 Bubble reply trigger ➜ stock_id: {stock_id} ➜ price: {response.get('price', '--')}")
            logger.info(f"📦 LINE Flex Bubble送出中 ➜ stock_id: {stock_id}")

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=f"{stock_id} 查價結果", contents=bubble)
            )
            
            logger.info(f"✅ reply 查價完成 ➜ 回覆股票代號 {stock_id}")
"""
