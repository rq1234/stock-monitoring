import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Dashboard from "@/pages/Dashboard";
import AgentPage from "@/pages/AgentPage";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        {/* 🔝 Navigation Bar */}
        <nav className="bg-gray-800 text-white px-6 py-3 flex justify-between items-center">
          <h1 className="font-bold text-lg">📊 Portfolio Monitor</h1>
          <div className="flex gap-4">
            <Link
              to="/"
              className="hover:text-blue-400 transition"
            >
              Dashboard
            </Link>
            <Link
              to="/agent"
              className="hover:text-blue-400 transition"
            >
              Agent Chat
            </Link>
          </div>
        </nav>

        {/* Main Content */}
        <div className="flex-1 p-6 bg-gray-100">
          <Routes>
            {/* Default dashboard */}
            <Route path="/" element={<Dashboard />} />

            {/* MCP Agent chat page */}
            <Route path="/agent" element={<AgentPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
