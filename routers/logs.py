# routers/logs.py

def router_trace_visualizer(stock_id: str, source: str, level: str, metadata: dict):
    print(f"\n🔍 [Router Trace Visualizer]")
    print(f"➤ 股票代號：{stock_id}")
    print(f"➤ fallback來源：{source}")
    print(f"➤ fallback階層：{level}")
    print(f"➤ 成交價：{metadata.get('收盤')}")
    print(f"➤ 漲跌幅：{metadata.get('漲跌')} ➤ 資料時間：{metadata.get('資料時間')}")
    print(f"➤ EPS：{metadata.get('EPS')} ➤ 本益比：{metadata.get('本益比')} ➤ 產業別：{metadata.get('產業別')}")
    print(f"✅ [End of Trace]\n")
