import React from "react";

interface Filing {
  date: string;
  accession: string;
  url: string;
  summary?: string;
  formType?: string; // ✅ make sure we capture the form type too
}

interface FilingsListProps {
  filings: Filing[];
  loading: boolean;
}

// ✅ Classification helper
const classifyFiling = (filing: Filing): "Warning" | "Positive" | "Neutral" => {
  const text = `${filing.formType || ""} ${filing.summary || ""}`.toLowerCase();

  // 🚨 Dilution risk → 424B3 filings, offerings, warrants, issuable shares
  // 🚨 Dilution risk → only if it's *new* issuance, not just historical mention
  if (
    text.includes("424b3") ||
    (text.includes("offering") && text.includes("shares")) || // "offering shares"
    text.includes("issuable upon exercise") || // specific dilution wording
    text.includes("warrants exercisable") // only if warrants can be converted
  ) {
    return "Warning";
  }

  // ✅ Positive signals → approvals, partnerships, revenue, profit
  if (
    text.includes("approval") ||
    text.includes("partnership") ||
    text.includes("revenue growth") ||
    text.includes("profit") ||
    text.includes("positive results")
  ) {
    return "Positive";
  }

  // ➖ Default
  return "Neutral";
};

const labelStyles: Record<"Warning" | "Positive" | "Neutral", string> = {
  Warning: "bg-red-100 text-red-800 border border-red-300",
  Positive: "bg-green-100 text-green-800 border border-green-300",
  Neutral: "bg-gray-100 text-gray-800 border border-gray-300",
};

const FilingsList: React.FC<FilingsListProps> = ({ filings, loading }) => {
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
        <p className="text-gray-600 dark:text-gray-300">Loading filings...</p>
      </div>
    );
  }

  if (!filings || filings.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
        <p className="text-gray-600 dark:text-gray-300">
          No recent filings found.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">
        📑 Latest SEC Filings
      </h2>
      <div className="space-y-4">
        {filings.map((filing, idx) => {
          const label = classifyFiling(filing);

          return (
            <div
              key={idx}
              className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-700 relative"
            >
              {/* Label box in top-right */}
              <div
                className={`absolute top-2 right-2 px-2 py-1 rounded-md text-xs font-semibold ${labelStyles[label]}`}
              >
                {label}
              </div>

              <p className="text-sm text-gray-500 dark:text-gray-400">
                {filing.date} {filing.formType ? `• ${filing.formType}` : ""}
              </p>
              <a
                href={filing.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 font-semibold hover:underline"
              >
                Accession {filing.accession}
              </a>
              {filing.summary && (
                <p className="mt-2 text-gray-700 dark:text-gray-200">
                  {filing.summary}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FilingsList;



