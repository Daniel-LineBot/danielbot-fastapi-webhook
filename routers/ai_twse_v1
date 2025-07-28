import httpx

async def get_twse_price(stock_id: str, date: str = None) -> dict:
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()
        for item in data:
            if item["證券代號"] == stock_id:
                return {
                    "name": item["證券名稱"],
                    "price": item["收盤價"],
                    "open": item["開盤價"],
                    "high": item["最高價"],
                    "low": item["最低價"],
                    "volume": item["成交股數"],
                    "date": item["日期"],
                    "source": "TWSE"
                }
        return {"error": "查無資料"}

async def get_twse_dividend(stock_id: str) -> dict:
    url = "https://openapi.twse.com.tw/v1/opendata/t187ap45_L"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()
        for item in data:
            if item["公司代號"] == stock_id:
                return {
                    "year": item["年度"],
                    "cash_dividend": item["現金股利"],
                    "stock_dividend": item["股票股利"],
                    "ex_dividend_date": item["除權息交易日"],
                    "source": "TWSE"
                }
        return {"error": "查無配息資料"}
