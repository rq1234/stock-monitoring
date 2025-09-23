import React from "react";
import { Loader2 } from "lucide-react";
import {
  Table, TableHeader, TableRow, TableHead, TableBody, TableCell,
} from "@/components/ui/table";
import DashboardCard from "@/components/DashboardCard";

interface Props {
  anomalies: any[];
  loading: boolean;
}

const AnomalyTable: React.FC<Props> = ({ anomalies, loading }) => {
  return (
    <DashboardCard title="Detected Anomalies">
      {loading ? (
        <Loader2 className="animate-spin text-gray-500" />
      ) : anomalies.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Description</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {anomalies.map((a, idx) => (
              <TableRow key={idx}>
                <TableCell>{a.trade_date}</TableCell>
                <TableCell>{a.anomaly_type}</TableCell>
                <TableCell>{a.description}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <p className="text-gray-500">No anomalies found</p>
      )}
    </DashboardCard>
  );
};

export default AnomalyTable;
