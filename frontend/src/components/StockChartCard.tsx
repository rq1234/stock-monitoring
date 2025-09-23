import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { getStockPrice } from "@/lib/mcpClient";

interface StockChartCardProps {
  ticker: string | null;
}

const StockChartCard: React.FC<StockChartCardProps> = ({ ticker }) => {
  const [data, setData] = useState<any[]>([]);
  const [latestPrice, setLatestPrice] = useState<number | null>(null);
  const [changeAbs, setChangeAbs] = useState<number | null>(null);
  const [changePct, setChangePct] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState("30d");

  // Available ranges
  const ranges = [
    { label: "1D", value: "1d" },
    { label: "5D", value: "5d" },
    { label: "30D", value: "30d" },
    { label: "3M", value: "3mo" },
    { label: "6M", value: "6mo" },
    { label: "1Y", value: "1y" },
  ];

  // Axis color depending on theme
  const axisColor = window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "#e5e7eb" // light gray in dark mode
    : "#000000"; // black in light mode

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);
    getStockPrice(ticker, timeRange)
      .then((res) => {
        const prices = res?.prices || [];
        setData(prices);

        if (prices.length > 0) {
          const first = prices[0].close;
          const last = prices[prices.length - 1].close;

          setLatestPrice(last);
          setChangeAbs(last - first);
          setChangePct(((last - first) / first) * 100);
        }
      })
      .finally(() => setLoading(false));
  }, [ticker, timeRange]);

  return (
    <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl shadow-md">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
          Price & Chart
        </h2>
        <select
          className="px-3 py-1 rounded-lg border dark:bg-gray-800 dark:text-white"
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
        >
          {ranges.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      {/* Loading / no data */}
      {loading || !latestPrice ? (
        <div className="text-gray-500">Select a ticker to view chart</div>
      ) : (
        <>
          {/* Current Price */}
          <div className="flex items-baseline mb-4">
            <span className="text-2xl font-bold text-green-500 dark:text-green-400">
              ${latestPrice.toFixed(2)}
            </span>
            {changeAbs !== null && changePct !== null && (
              <span
                className={`ml-3 text-sm font-medium ${
                  changeAbs >= 0
                    ? "text-green-500 dark:text-green-400"
                    : "text-red-500 dark:text-red-400"
                }`}
              >
                {changeAbs >= 0 ? "+" : ""}
                {changeAbs.toFixed(2)} ({changePct.toFixed(2)}%)
              </span>
            )}
          </div>

          {/* Chart */}
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke={axisColor}
                strokeOpacity={0.1}
              />
              <XAxis
                dataKey="date"
                stroke={axisColor}
                tick={{ fontSize: 12, fill: axisColor }}
                axisLine={{ stroke: axisColor }}
                tickLine={{ stroke: axisColor }}
                angle={-45}
                textAnchor="end"
                height={50}
              />
              <YAxis
                stroke={axisColor}
                tick={{ fontSize: 12, fill: axisColor }}
                axisLine={{ stroke: axisColor }}
                tickLine={{ stroke: axisColor }}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  color: "white",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "white" }}
                formatter={(val: number) => [`$${val.toFixed(2)}`, "Close"]}
              />
              <Line
                type="monotone"
                dataKey="close"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
};

export default StockChartCard;





