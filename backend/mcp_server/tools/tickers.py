# backend/mcp_server/tools/tickers.py
from backend.mcp_server import mcp
from backend.db.supabase_client import supabase

@mcp.tool()
def list_tickers() -> dict:
    """
    Fetch distinct list of tickers from Supabase `spac_list`.
    Returns:
        dict: { "tickers": ["DSY", "SOFI", ...] }
    """
    try:
        if not supabase:
            raise RuntimeError("Supabase client is not initialized. Check supabase_client.py")

        # Query Supabase table
        response = supabase.table("spac_list").select("ticker").execute()

        # Log the full raw response
        print("✅ DEBUG - raw Supabase response:", response, flush=True)

        rows = response.data
        if rows is None:
            raise RuntimeError(f"Supabase returned no data. Response: {response}")

        # Log rows
        print("✅ DEBUG - rows returned from Supabase:", rows, flush=True)

        # Deduplicate + uppercase tickers
        tickers = sorted(
            {row["ticker"].upper() for row in rows if row.get("ticker")}
        )

        # Final check
        if not tickers:
            print("⚠️ WARNING - No tickers found in spac_list table.", flush=True)

        print("✅ DEBUG - processed tickers:", tickers, flush=True)

        return {"tickers": tickers}

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ ERROR in list_tickers: {e}", flush=True)
        return {"error": f"Failed to fetch tickers: {e}"}





