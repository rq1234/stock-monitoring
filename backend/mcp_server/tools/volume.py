# backend/mcp_server/tools/volume.py
import yfinance as yf
from backend.mcp_server import mcp

@mcp.tool()
def get_volume_history(ticker: str, days: int = 30, interval: str = "1d"):
    """
    Fetch historical daily volume for a given ticker.
    """
    period = f"{days}d"  # convert number -> yfinance period string
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)

    if hist.empty:
        return {"error": f"No volume data for {ticker} with period={period}, interval={interval}"}

    history = [
        {"date": str(idx.date()), "volume": int(row["Volume"])}
        for idx, row in hist.iterrows()
    ]

    return {"ticker": ticker.upper(), "days": days, "interval": interval, "history": history}






