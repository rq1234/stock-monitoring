// src/lib/mcpClient.ts
const MCP_BASE_URL = "http://localhost:8000"; // MCP HTTP server (FastAPI)

// --- Generic call wrapper ---
async function callMCP<T = any>(
  tool: string,
  args: Record<string, any> = {}
): Promise<T | null> {
  try {
    const resp = await fetch(`${MCP_BASE_URL}/tools/${tool}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ args }), // 🔑 HTTP server expects { args: {...} }
    });

    if (!resp.ok) {
      console.error(`❌ MCP ${tool} failed:`, await resp.text());
      return null;
    }

    return (await resp.json()) as T;
  } catch (err) {
    console.error(`⚠️ MCP ${tool} error:`, err);
    return null;
  }
}

// --- Tool wrappers ---

// ✅ List all tickers from Supabase
export async function listTickers(): Promise<string[]> {
  const res = await callMCP<{ tickers: string[] }>("list_tickers");
  return res?.tickers || [];
}

// ✅ Latest stock price
export async function getStockPrice(
  ticker: string,
  period: string = "1mo",
  interval: string = "1d"
) {
  const res = await fetch("http://localhost:8000/tools/get_stock_price", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ args: { ticker, period, interval } }),
  });
  return res.json();
}


// ✅ Volume history (from Supabase)

export async function getVolumeHistory(ticker: string, days: number) {
  return callMCP("get_volume_history", { ticker, days });
}

// ✅ Full stock history with support/resistance
export async function getStockHistory(
  ticker: string,
  period: string = "1mo",
  interval: string = "1d"
): Promise<{
  ticker: string;
  period: string;
  interval: string;
  prices: any[];
  support: number;
  resistance: number;
} | null> {
  return await callMCP("get_stock_history", { ticker, period, interval });
}

// ✅ Anomalies
export async function detectAnomalies(
  ticker: string
): Promise<{ ticker: string; anomalies: any[] } | null> {
  return await callMCP("detect_anomalies", { ticker });
}

// ✅ 8-K Filings
export async function getFilings(
  ticker: string,
  formTypes: string[] = ["8-K"],
  limit: number = 3,
  summarize: boolean = false
): Promise<{ ticker: string; filings: any[] } | null> {
  return await callMCP("get_filings", { ticker, form_types: formTypes, limit, summarize });
}

// lib/mcpClient.ts

export async function getAlertsMarkdown(startDate?: string, endDate?: string) {
  const res = await fetch("http://localhost:8000/tools/get_alerts_markdown", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      args: {
        start_date: startDate,
      },
    }),
  });

  if (!res.ok) {
    console.error("❌ Failed to fetch alerts markdown:", res.statusText);
    return { date: "", count: 0, markdown: "" };
  }

  return res.json(); // { date, count, markdown }
}







