#utils/formatter_finmind.py


def format_dividend(data: dict) -> str:
    # 判斷除息日是否來自備註推斷（含中文或民國年格式）
    ex_date_raw = data.get("ex_dividend_date", "-")
    if "年" in ex_date_raw or ex_date_raw.startswith("202"):  # 推斷邏輯可以更精細
        ex_date_label = f"📆 除息日（備註推斷）：{ex_date_raw}"
    else:
        ex_date_label = f"📢 除息日（公告日期）：{ex_date_raw}"

    return f'''
📊 {data["year"]} 配息資訊
💰 現金股利：{data["cash_dividend"]}
📈 股票股利：{data["stock_dividend"]}
{ex_date_label}
來源：{data["source"]}
'''.strip()
