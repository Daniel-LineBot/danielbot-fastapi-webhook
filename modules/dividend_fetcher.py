async def fetch_twse_dividend(stock_id, year=None):
    # TODO: 串接TWSE API
    # 範例假資料
    return {"source": "TWSE", "data": f"{stock_id} {year or ''} TWSE配息資料"}

async def fetch_finmind_dividend(stock_id, year=None):
    # TODO: 串接FinMind API
    return {"source": "FinMind", "data": f"{stock_id} {year or ''} FinMind配息資料"}

async def fetch_central_depository_dividend(stock_id, year=None):
    # TODO: 串接集保API
    return {"source": "CentralDepository", "data": f"{stock_id} {year or ''} 集保配息資料"}

async def fetch_all_dividend(stock_id, year=None):
    result = []
    result.append(await fetch_twse_dividend(stock_id, year))
    result.append(await fetch_finmind_dividend(stock_id, year))
    result.append(await fetch_central_depository_dividend(stock_id, year))
    return result