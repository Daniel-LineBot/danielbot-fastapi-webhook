from linebot.models import BubbleContainer, BoxComponent, TextComponent, FlexSendMessage

def reply_bubble_builder(response: dict) -> BubbleContainer:
    stock_id = response.get("stock_id", "未知代碼")
    price = response.get("price", "--")
    change = response.get("change", "--")
    source = response.get("source", "fallback")
    timestamp = response.get("timestamp", "--")

    bubble = BubbleContainer(
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text=f"📈 查詢結果 - {stock_id}", weight="bold", size="md"),
                TextComponent(text=f"成交價：{price} 元", size="sm"),
                TextComponent(text=f"漲跌：{change}", size="sm"),
                TextComponent(text=f"來源：{source}", size="xs", color="#AAAAAA"),
                TextComponent(text=f"資料時間：{timestamp}", size="xs", color="#AAAAAA"),
            ]
        )
    )
    return bubble
