# backend/mcp_server/tools/price.py
import yfinance as yf
import numpy as np
from backend.mcp_server import mcp


@mcp.tool()
def get_stock_price(ticker: str, period: str = "1mo", interval: str = "1d") -> dict:
    """
    Fetch stock historical data (OHLCV) and compute support/resistance.

    Args:
        ticker (str): Stock symbol (e.g. "SOFI").
        period (str): Lookback window ("1d", "5d", "1mo", "3mo", "6mo", "1y", etc.).
        interval (str): Candle size ("1d", "1h", "30m", etc.).

    Returns:
        dict: {
            "ticker": ...,
            "period": ...,
            "interval": ...,
            "prices": [{date, open, high, low, close, volume}, ...],
            "support": ...,
            "resistance": ...
        }
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)

    if hist.empty:
        return {"error": f"No data for {ticker} with period={period}, interval={interval}"}

    # Convert rows to JSON-serializable list
    prices = [
        {
            "date": str(idx.date()),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]),
        }
        for idx, row in hist.iterrows()
    ]

    # Compute support/resistance from close prices
    closes = hist["Close"].values
    support = float(np.percentile(closes, 25))   # lower quartile
    resistance = float(np.percentile(closes, 75)) # upper quartile
    latest_close = float(closes[-1])

    return {
        "ticker": ticker.upper(),
        "period": period,
        "interval": interval,
        "prices": prices,
        "support": support,
        "resistance": resistance,
        "price": latest_close, 
    }



