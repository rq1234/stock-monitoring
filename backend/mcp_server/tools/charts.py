import matplotlib.pyplot as plt
import io, base64
from backend.db.supabase_client import supabase
from backend.mcp_server import mcp

@mcp.tool()
def plot_volume_chart(ticker: str, days: int = 10) -> dict:
    """
    Generate a volume chart for the given ticker.
    Returns a base64-encoded PNG.
    """
    rows = (
        supabase.table("spac_data")
        .select("trade_date, volume")
        .eq("ticker", ticker.upper())
        .order("trade_date", desc=False)
        .limit(days)
        .execute()
        .data
    )

    if not rows:
        return {"error": f"No data for {ticker}"}

    dates = [r["trade_date"] for r in rows]
    volumes = [r["volume"] for r in rows]

    plt.figure(figsize=(6, 4))
    plt.bar(dates, volumes)
    plt.title(f"{ticker.upper()} Volume (last {days} days)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    return {"ticker": ticker.upper(), "chart": img_base64}
