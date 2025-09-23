# tools/sec_utils.py
import requests

SEC_HEADERS = {
    "User-Agent": "StockMonitorApp (contact: youremail@example.com)"
}

TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"

def lookup_cik(ticker: str) -> dict:
    """
    Look up CIK and company title for a given ticker.
    """
    resp = requests.get(TICKER_CIK_URL, headers=SEC_HEADERS)
    if resp.status_code != 200:
        raise ValueError(f"SEC ticker lookup failed {resp.status_code}")

    data = resp.json()
    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker.upper():
            return {
                "cik": str(entry["cik_str"]).zfill(10),  # pad to 10 digits
                "title": entry.get("title", "")
            }

    raise ValueError(f"Could not find CIK for ticker {ticker}")