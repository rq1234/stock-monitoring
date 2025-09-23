import React from "react";

interface DashboardCardProps {
  title: string;
  children: React.ReactNode;
}

const DashboardCard: React.FC<DashboardCardProps> = ({ title, children }) => {
  return (
    <div className="rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-300">
      {/* Header */}
      <div className="px-6 py-3 bg-indigo-600 dark:bg-indigo-700 rounded-t-2xl">
        <h2 className="text-lg font-semibold text-white">{title}</h2>
      </div>

      {/* Content */}
      <div className="p-6 text-gray-800 dark:text-gray-100">
        {children}
      </div>
    </div>
  );
};

export default DashboardCard;

