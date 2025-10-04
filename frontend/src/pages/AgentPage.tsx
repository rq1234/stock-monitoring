import React, { useState, useRef, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const MCP_BASE_URL =
  import.meta.env.VITE_MCP_BASE_URL || "http://localhost:8000";

const MyChartComponent = ({ data, ticker }: { data: any[]; ticker: string }) => (
  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md mb-4">
    <h3 className="font-bold mb-2">{ticker} Volume Chart</h3>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

const AgentPage: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage() {
    if (!input.trim()) return;

    const newMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, newMsg]);
    setLoading(true);

    try {
      const payload = { query: input };

      const res = await fetch(`${MCP_BASE_URL}/mcp/agent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      let msg;
      const answer = data.answer;

      if (typeof answer === "string") {
        msg = { role: "assistant", type: "text", content: answer };
      } else if (answer?.type === "chart") {
        msg = { role: "assistant", ...answer };
      } else if (answer?.type === "filings") {
        msg = { role: "assistant", ...answer };
      } else if (answer?.type === "anomalies") {
        msg = { role: "assistant", ...answer };
      } else {
        msg = { role: "assistant", type: "text", content: JSON.stringify(answer) };
      }

      setMessages((prev) => [...prev, msg]);
    } catch (err) {
      console.error("⚠️ MCP Agent error:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", type: "error", content: "⚠️ Error talking to agent" },
      ]);
    } finally {
      setInput("");
      setLoading(false);
    }
  }

  function handleKeyPress(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !loading) sendMessage();
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <h1 className="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">🤖 MCP Agent Chat</h1>

      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-4 h-[70vh] overflow-y-auto mb-4">
        {messages.map((m, i) => (
          <div key={i} className="mb-4">
            {m.role === "assistant" && m.type === "chart" ? (
              <MyChartComponent data={m.data} ticker={m.ticker} />
            ) : m.role === "assistant" && m.type === "filings" ? (
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded shadow">
                <h3 className="font-bold">{m.ticker} Filings</h3>
                {m.filings.map((f: any, idx: number) => (
                  <p key={idx}>
                    {f.date}:{" "}
                    <a
                      href={f.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 underline"
                    >
                      {f.accession}
                    </a>
                  </p>
                ))}
              </div>
            ) : (
              <div
                className={
                  m.role === "user"
                    ? "text-blue-600"
                    : "text-gray-800 dark:text-gray-200"
                }
              >
                <b>{m.role === "user" ? "You" : "Agent"}:</b> {m.content}
              </div>
            )}
          </div>
        ))}
        {loading && <p className="italic text-gray-400">Thinking...</p>}
        <div ref={chatEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 p-2 border rounded-lg dark:bg-gray-700 dark:text-white"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Ask me about tickers, filings, anomalies..."
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg"
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
};

export default AgentPage;


