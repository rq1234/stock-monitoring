import React from "react";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import DashboardCard from "@/components/DashboardCard";

interface Props {
  tickers: string[];
  selectedTicker: string | null;
  setSelectedTicker: (ticker: string | null) => void; // ✅ allow null reset
  onRefresh: () => void;
}

const TickerSelector: React.FC<Props> = ({
  tickers,
  selectedTicker,
  setSelectedTicker,
  onRefresh,
}) => {
  return (
    <DashboardCard title="Select Ticker">
      <div className="flex items-center space-x-4">
        <Select
          value={selectedTicker || ""}
          onValueChange={(val) => setSelectedTicker(val || null)}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Select Ticker" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__none__">-- None --</SelectItem> {/* ✅ valid value */}
            {tickers.map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button
          onClick={onRefresh}
          disabled={!selectedTicker}
          variant="secondary"
        >
          Refresh
        </Button>

        <Button
          onClick={() => setSelectedTicker(null)} // ✅ resets dropdown
          variant="outline"
        >
          Reset
        </Button>
      </div>
    </DashboardCard>
  );
};

export default TickerSelector;


