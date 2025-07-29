#utils/formatter_twse.py


def format_dividend(data: dict) -> str:
    return f'''
📊 {data["year"]} 配息資訊
💰 現金股利：{data["cash_dividend"]}
📈 股票股利：{data["stock_dividend"]}
📆 除權息日：{data["ex_dividend_date"]}
來源：{data["source"]}
'''.strip()
