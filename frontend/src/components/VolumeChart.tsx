// VolumeChart.tsx
import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

// ✅ Type
interface VolumeChartProps {
  ticker: string;
  fetchVolume: (days: number) => Promise<any[]>;
}

// ✅ Utility: Compute 7-day moving average
function addMovingAverage(data: any[], windowSize = 7) {
  return data.map((d, i) => {
    if (i < windowSize - 1) return { ...d, ma7: null };
    const slice = data.slice(i - windowSize + 1, i + 1);
    const avg = slice.reduce((sum, row) => sum + row.volume, 0) / windowSize;
    return { ...d, ma7: Math.round(avg) };
  });
}

// ✅ Utility: format big numbers to K / M
function formatVolume(value: number) {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`;
  return value.toString();
}

// ✅ Utility: shorten date (2025-09-12 → Sep 12)
function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

const VolumeChart: React.FC<VolumeChartProps> = ({ ticker, fetchVolume }) => {
  const [data, setData] = useState<any[]>([]);
  const [days, setDays] = useState<number>(30);
  const [chartType, setChartType] = useState<"bar" | "line">("bar");

  useEffect(() => {
    if (!ticker) return;
    fetchVolume(days).then((res) => {
      setData(addMovingAverage(res, 7));
    });
  }, [ticker, days, fetchVolume]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">
        📊 Volume History ({ticker})
      </h2>

      {/* Controls */}
      <div className="flex space-x-2 mb-4">
        {[5, 30, 90, 180].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-3 py-1 rounded ${
              d === days
                ? "bg-blue-500 text-white"
                : "bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100"
            }`}
          >
            {d}d
          </button>
        ))}

        {/* Toggle chart type */}
        <button
          onClick={() =>
            setChartType((prev) => (prev === "bar" ? "line" : "bar"))
          }
          className="ml-auto px-3 py-1 rounded bg-indigo-500 text-white hover:bg-indigo-600"
        >
          Switch to {chartType === "bar" ? "Line" : "Bar"}
        </button>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        {chartType === "bar" ? (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tickFormatter={formatDate} />
            <YAxis tickFormatter={formatVolume} />
            <Tooltip
              formatter={(value: number) => [formatVolume(value), "Volume"]}
              labelFormatter={(label) => `Date: ${formatDate(label)}`}
            />
            <Legend />
            <Bar dataKey="volume" fill="#3b82f6" name="Daily Volume" />
            <Line
              type="monotone"
              dataKey="ma7"
              stroke="#f97316"
              strokeWidth={2}
              dot={false}
              name="7d MA"
            />
          </BarChart>
        ) : (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tickFormatter={formatDate} />
            <YAxis tickFormatter={formatVolume} />
            <Tooltip
              formatter={(value: number) => [formatVolume(value), "Volume"]}
              labelFormatter={(label) => `Date: ${formatDate(label)}`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="volume"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              name="Daily Volume"
            />
            <Line
              type="monotone"
              dataKey="ma7"
              stroke="#f97316"
              strokeWidth={2}
              dot={false}
              name="7d MA"
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default VolumeChart;






