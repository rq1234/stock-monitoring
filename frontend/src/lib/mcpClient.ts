// src/lib/mcpClient.ts

// Use env variable for MCP base URL
const MCP_BASE_URL =
  import.meta.env.VITE_MCP_BASE_URL || "http://localhost:8000";

console.log("Raw VITE_MCP_BASE_URL:", import.meta.env.VITE_MCP_BASE_URL);
console.log("Final MCP_BASE_URL:", MCP_BASE_URL);

// --- Generic call wrapper ---
async function callMCP<T = any>(
  tool: string,
  args: Record<string, any> = {}
): Promise<T | null> {
  try {
    const resp = await fetch(`${MCP_BASE_URL}/tools/${tool}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ args }), // 🔑 backend expects { args: {...} }
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

// ✅ List all tickers
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
  return callMCP("get_stock_price", { ticker, period, interval });
}

// ✅ Volume history
export async function getVolumeHistory(ticker: string, days: number) {
  return callMCP("get_volume_history", { ticker, days });
}

// ✅ Full stock history
export async function getStockHistory(
  ticker: string,
  period: string = "1mo",
  interval: string = "1d"
) {
  return callMCP("get_stock_history", { ticker, period, interval });
}

// ✅ Anomalies
export async function detectAnomalies(ticker: string) {
  return callMCP("detect_anomalies", { ticker });
}

// ✅ 8-K Filings
export async function getFilings(
  ticker: string,
  formTypes: string[] = ["8-K"],
  limit: number = 3,
  summarize: boolean = false
) {
  return callMCP("get_filings", { ticker, form_types: formTypes, limit, summarize });
}

// ✅ Alerts Markdown
export async function getAlertsMarkdown(startDate?: string, endDate?: string) {
  return callMCP("get_alerts_markdown", { start_date: startDate, end_date: endDate });
}








