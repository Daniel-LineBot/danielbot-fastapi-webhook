import requests
from bs4 import BeautifulSoup

def name_to_id(query: str) -> str | None:
    twse_url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    response = requests.get(twse_url)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")[1:]  # skip header

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5: continue
        code_name = cols[0].text.strip()
        if not code_name: continue
        if query in code_name:
            stock_id = code_name.split("　")[0].strip()
            return stock_id
    return None  # ❌ 查不到代碼
