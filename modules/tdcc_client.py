# modules/tdcc_client.py

import requests

def get_cdib_dividend(stock_id: str) -> dict:
    endpoint = "https://www.tdcc.com.tw/smWeb/QryStockAjax.do"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.tdcc.com.tw/smWeb/QryStock.jsp"
    }
    payload = {
        "encodeStockId": stock_id,
        "isnew": "true"
    }

    try:
        response = requests.post(endpoint, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()

        # TODO: 根據 data 結構整理股東資訊、股本、集保比例…
        return {
            "source": "集保",
            "raw": data
        }

    except Exception as e:
        return {"source": "集保", "error": str(e)}
