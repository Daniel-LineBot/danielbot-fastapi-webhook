def get_query_metadata(text: str) -> dict:
    return {
        "stock_id": extract_stock_id(text),
        "query_type": normalize_query_type(text),
        "year": extract_year(text),  # optional
        "raw": text
    }
