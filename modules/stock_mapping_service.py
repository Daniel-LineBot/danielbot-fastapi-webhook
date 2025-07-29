class StockNameResolver:
    def __init__(self):
        self.name_to_id = {}  # 可載入 TWSE 初始值
        self.last_updated = None

    def load_from_twse(self):
        # 定時載入 TWSE 名稱與代碼 csv
        ...

    def query_from_finmind(self, name: str) -> str | None:
        # 呼叫 FinMind 查公司代碼
        ...

    def query_from_tdcc(self, name: str) -> str | None:
        # 呼叫集保 API 查代碼（限流或 fallback）
        ...

    def get_stock_id(self, name: str) -> str | None:
        if name in self.name_to_id:
            return self.name_to_id[name]
        # fallback 到 API 查詢
        return self.query_from_finmind(name) or self.query_from_tdcc(name)
