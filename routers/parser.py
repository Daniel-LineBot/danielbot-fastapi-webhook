# routers/parser.py

from bs4 import BeautifulSoup

def parse_eps_pe_industry(raw_html: str) -> dict:
    soup = BeautifulSoup(raw_html, "html.parser")

    result = {
        "EPS": "N/A",
        "本益比": "N/A",
        "產業別": "N/A"
    }

    # EPS ➜ 公開資訊或 Goodinfo 表格中
    eps_box = soup.find(text=lambda t: t and "EPS" in t)
    if eps_box:
        result["EPS"] = eps_box.parent.find_next("td").text.strip()

    # 本益比 ➜ PE Ratio文字附近
    pe_box = soup.find(text=lambda t: t and ("本益比" in t or "PE Ratio" in t))
    if pe_box:
        result["本益比"] = pe_box.parent.find_next("td").text.strip()

    # 產業別 ➜ TWSE或 Goodinfo頁面有 "產業類別"
    sector = soup.find(text=lambda t: t and ("產業類別" in t or "Industry" in t))
    if sector:
        result["產業別"] = sector.parent.find_next("td").text.strip()

    return result
