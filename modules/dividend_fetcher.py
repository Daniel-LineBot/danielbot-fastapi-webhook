
async def fetch_twse_dividend(stock_id, year=None):
    # TODO: 串接 TWSE API
    return {
        "source": "TWSE",
        "data": {
            "year": year or 2024,
            "cash_dividend": "1.5",
            "stock_dividend": "0.0",
            "ex_dividend_date": "2024-07-01",
            "source": "TWSE"
        }
    }

async def fetch_finmind_dividend(stock_id, year=None):
    # TODO: 串接 FinMind API
    return {
        "source": "FinMind",
        "data": {
            "year": year or 2024,
            "cash_dividend": "1.7",
            "stock_dividend": "0.0",
            "ex_dividend_date": "2024-06-28",
            "source": "FinMind"
        }
    }

async def fetch_central_depository_dividend(stock_id, year=None):
    # TODO: 串接 集保 API
    return {
        "source": "TDCC",
        "data": {
            "year": year or 2024,
            "cash_dividend": "1.6",
            "stock_dividend": "0.0",
            "ex_dividend_date": "2024-06-30",
            "source": "TDCC"
        }
    }

async def fetch_all_dividend(stock_id, year=None):
    result = []
    result.append(await fetch_twse_dividend(stock_id, year))
    result.append(await fetch_finmind_dividend(stock_id, year))
    result.append(await fetch_central_depository_dividend(stock_id, year))
    return result
