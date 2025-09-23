import yfinance as yf
from backend.db.supabase_client import supabase
from datetime import datetime, date
from typing import Dict, List


def fetch_and_store_daily_data(state: Dict = None) -> Dict:
    """
    Fetch OHLCV + metadata for SPAC tickers, update Supabase,
    and return workflow state for downstream agents.

    Returns state dict with:
    {
        "status": "ok" | "empty",
        "tickers": [...],
        "updated": [...],
        "anomalies": [...],   # always present for consistency
    }
    """
    if state is None:
        state = {}

    tickers = supabase.table("spac_list").select("ticker").execute().data
    if not tickers:
        print(" No tickers found in spac_list")
        state.update({"status": "empty", "tickers": [], "updated": [], "anomalies": []})
        return state

    updated: List[Dict] = []

    for row in tickers:
        ticker = row["ticker"]
        stock = yf.Ticker(ticker)

        # --- 1. Metadata enrichment ---
        try:
            info = stock.info or {}
            country = info.get("country", "Unknown")
            exchange = info.get("exchange", "Unknown")
            ipo_raw = info.get("ipoExpectedDate") or info.get("firstTradeDateEpochUtc")

            ipo_date = None
            if ipo_raw:
                try:
                    if isinstance(ipo_raw, int):
                        ipo_date = datetime.fromtimestamp(ipo_raw).date()
                    elif isinstance(ipo_raw, str):
                        ipo_date = datetime.strptime(ipo_raw, "%Y-%m-%d").date()
                except Exception:
                    ipo_date = None

            supabase.table("spac_list").update({
                "country": country,
                "exchange": exchange,
                "ipo_date": ipo_date.isoformat() if ipo_date else None
            }).eq("ticker", ticker).execute()

            print(f" Metadata updated for {ticker}: {country}, IPO={ipo_date}, Exchange={exchange}")
        except Exception as e:
            print(f" Failed metadata update for {ticker}: {e}")

        # --- 2. Latest finalized OHLCV (avoid intraday candles) ---
        try:
            hist = stock.history(period="7d")  # last week to be safe
            if hist.empty:
                print(f" No OHLCV data for {ticker}")
                continue

            last = hist.iloc[-1]
            if last.name.date() == date.today():
                # If today is incomplete → use yesterday’s
                if len(hist) > 1:
                    last = hist.iloc[-2]

            trade_date = last.name.date()

            supabase.table("spac_data").upsert({
                "ticker": ticker,
                "trade_date": trade_date.isoformat(),
                "open": float(last["Open"]),
                "high": float(last["High"]),
                "low": float(last["Low"]),
                "close": float(last["Close"]),
                "volume": int(last["Volume"])
            }).execute()

            print(f" Stored OHLCV for {ticker} on {trade_date}")
            updated.append({"ticker": ticker, "trade_date": trade_date.isoformat()})

        except Exception as e:
            print(f" Failed OHLCV fetch for {ticker}: {e}")

    # --- Build final state ---
    state.update({
        "status": "ok",
        "tickers": [row["ticker"] for row in tickers],
        "updated": updated,
        "anomalies": state.get("anomalies", [])  
    })
    return state


# For standalone runs (outside LangGraph)
if __name__ == "__main__":
    final_state = fetch_and_store_daily_data()
    print("Final state:", final_state)





