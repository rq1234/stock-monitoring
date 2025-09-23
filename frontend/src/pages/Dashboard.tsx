import React, { useEffect, useState } from "react";
import {
  listTickers,
  getVolumeHistory,
  detectAnomalies,
  getFilings,
  getAlertsMarkdown, // ✅ MCP client for alerts
} from "@/lib/mcpClient";

import TickerSelector from "@/components/TickerSelector";
import StockChartCard from "@/components/StockChartCard";
import VolumeChart from "@/components/VolumeChart";
import AnomalyTable from "@/components/AnomalyTable";
import FilingsList from "@/components/FilingsList";
import ErrorBoundary from "@/components/ErrorBoundary"; // ✅ import wrapper
import { Sun, Moon, Download } from "lucide-react";
import ReactMarkdown from "react-markdown"; // ✅ renders markdown nicely

// ---- Interfaces ----
interface AlertsMarkdownResponse {
  date: string;
  count: number;
  markdown: string;
}

const Dashboard: React.FC = () => {
  // ---- State ----
  const [tickers, setTickers] = useState<string[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);

  const [volumeData, setVolumeData] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [filings, setFilings] = useState<any[]>([]);

  const [loadingVolume, setLoadingVolume] = useState(false);
  const [loadingAnomalies, setLoadingAnomalies] = useState(false);
  const [loadingFilings, setLoadingFilings] = useState(false);

  const [darkMode, setDarkMode] = useState(false);

  // 🔔 Global Alerts
  const [alertsMarkdown, setAlertsMarkdown] = useState<string>("");
  const [loadingAlerts, setLoadingAlerts] = useState(false);
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  // ---- Load tickers on mount ----
  useEffect(() => {
    (async () => {
      const res = await listTickers();
      setTickers(res);
    })();
  }, []);

  // ---- Fetch per-ticker data ----
  const fetchData = async () => {
    if (!selectedTicker) return;

    setLoadingVolume(true);
    getVolumeHistory(selectedTicker, 10)
      .then((res) => setVolumeData(res?.history || []))
      .finally(() => setLoadingVolume(false));

    setLoadingAnomalies(true);
    detectAnomalies(selectedTicker)
      .then((res) => setAnomalies(res?.anomalies || []))
      .finally(() => setLoadingAnomalies(false));

    setLoadingFilings(true);
    getFilings(selectedTicker, ["8-K", "S-1", "S-8", "424B3", "4"], 5, true)
      .then((res) => setFilings(res?.filings || []))
      .finally(() => setLoadingFilings(false));
  };

  useEffect(() => {
    fetchData();
  }, [selectedTicker]);

  // ---- Fetch global alerts (markdown) ----
  const fetchAlerts = async () => {
    setLoadingAlerts(true);
    getAlertsMarkdown(startDate || undefined, endDate || undefined)
      .then((res: AlertsMarkdownResponse) =>
        setAlertsMarkdown(res?.markdown || "")
      )
      .finally(() => setLoadingAlerts(false));
  };

  useEffect(() => {
    fetchAlerts();
  }, [startDate, endDate]);

  // ---- Export Handlers ----
  const downloadFile = (filename: string, content: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportMarkdown = () => {
    const today = new Date().toISOString().split("T")[0];
    const md =
      alertsMarkdown || `# 📊 SPAC Alerts (${today})\n\n✅ No anomalies found.`;
    downloadFile(`spac_alerts_${today}.md`, md, "text/markdown");
  };

  const exportCSV = () => {
    const today = new Date().toISOString().split("T")[0];
    const lines = alertsMarkdown.split("\n").filter((l) => l.startsWith("- "));
    const header = "Ticker,Trade Date,Details\n";
    const rows = lines
      .map((l) => {
        const match = l.match(/\*\*(.*?)\*\* \((.*?)\) → (.*)/);
        if (match) {
          const [, ticker, date, details] = match;
          return `${ticker},${date},"${details.replace(/"/g, '""')}"`;
        }
        return "";
      })
      .filter(Boolean)
      .join("\n");

    downloadFile(`spac_alerts_${today}.csv`, header + rows, "text/csv");
  };

  // ---- Render ----
  return (
    <div className={`${darkMode ? "dark" : ""}`}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300 p-8 space-y-8">
        
        {/* Header with dark mode toggle */}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100">
            📊 Portfolio Monitoring Dashboard
          </h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
          >
            {darkMode ? (
              <Sun className="w-5 h-5 text-yellow-400" />
            ) : (
              <Moon className="w-5 h-5 text-gray-800" />
            )}
          </button>
        </div>

        {/* 🔔 Alerts Panel */}
        <ErrorBoundary fallback={<p>⚠️ Failed to load alerts.</p>}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">
                ⚡ Daily Alerts
              </h2>
              <div className="flex gap-2">
                <button
                  onClick={exportMarkdown}
                  className="flex items-center gap-1 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                >
                  <Download className="w-4 h-4" /> Markdown
                </button>
                <button
                  onClick={exportCSV}
                  className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <Download className="w-4 h-4" /> CSV
                </button>
              </div>
            </div>

            {/* Date Range Filters */}
            <div className="flex gap-4 mt-4">
              <div>
                <label className="block text-sm text-gray-600 dark:text-gray-400">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="mt-1 rounded-md border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-2"
                />
              </div>
              
              <button
                onClick={fetchAlerts}
                className="self-end px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                Refresh
              </button>
            </div>

            {/* Alerts Markdown */}
            {loadingAlerts ? (
              <p className="text-gray-500 mt-4">Loading alerts...</p>
            ) : alertsMarkdown ? (
              <div className="prose dark:prose-invert mt-4">
                <ReactMarkdown
                  components={{
                    a: ({ node, ...props }) => {
                      const ticker = props.href || "";
                      const isSelected = selectedTicker === ticker;

                      return (
                        <button
                          onClick={() => {
                            setSelectedTicker(ticker);
                            fetchData();
                          }}
                          style={{
                            background: isSelected ? "rgba(59, 130, 246, 0.1)" : "none",
                            border: "none",
                            color: isSelected ? "blue" : "inherit",
                            cursor: "pointer",
                            padding: "2px 4px",
                            borderRadius: "4px",
                            font: "inherit",
                          }}
                        >
                          {props.children}
                        </button>
                      );
                    },
                  }}
                >
                  {alertsMarkdown}
                </ReactMarkdown>
              </div>
            ) : (
              <p className="text-gray-500 mt-4">✅ No anomalies found in range.</p>
            )}
          </div>
        </ErrorBoundary>

        {/* Ticker Selector */}
        <ErrorBoundary fallback={<p>⚠️ Ticker selector failed.</p>}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
            <TickerSelector
              tickers={tickers}
              selectedTicker={selectedTicker}
              setSelectedTicker={setSelectedTicker}
              onRefresh={fetchData}
            />
          </div>
        </ErrorBoundary>

        {/* Unified price + chart */}
        <ErrorBoundary fallback={<p>⚠️ Stock chart failed.</p>}>
          <StockChartCard ticker={selectedTicker} />
        </ErrorBoundary>

        {/* Volume chart */}
        <ErrorBoundary fallback={<p>⚠️ Volume chart failed.</p>}>
          <VolumeChart
            ticker={selectedTicker || ""}
            fetchVolume={(days: number) =>
              getVolumeHistory(selectedTicker || "", days).then((res) => {
                console.log("[DEBUG] getVolumeHistory raw response:", res);
                return res?.history || [];
              })
            }
          />
        </ErrorBoundary>

        <ErrorBoundary fallback={<p>⚠️ Anomalies table failed.</p>}>
          <AnomalyTable anomalies={anomalies} loading={loadingAnomalies} />
        </ErrorBoundary>

        <ErrorBoundary fallback={<p>⚠️ Filings list failed.</p>}>
          <FilingsList filings={filings} loading={loadingFilings} />
        </ErrorBoundary>
      </div>
    </div>
  );
};

export default Dashboard;














