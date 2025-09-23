import { useState } from "react"

const tickers = ["AAPL", "TSLA", "AMZN", "MSFT"]

export default function Sidebar({ onSelect }: { onSelect: (ticker: string) => void }) {
  const [active, setActive] = useState("AAPL")

  return (
    <aside className="w-48 border-r h-screen bg-gray-50">
      <nav className="flex flex-col">
        {tickers.map((t) => (
          <button
            key={t}
            onClick={() => {
              setActive(t)
              onSelect(t)
            }}
            className={`px-4 py-2 text-left hover:bg-gray-200 ${
              active === t ? "bg-gray-300 font-semibold" : ""
            }`}
          >
            {t}
          </button>
        ))}
      </nav>
    </aside>
  )
}