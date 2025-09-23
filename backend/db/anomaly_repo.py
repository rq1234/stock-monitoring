alter table anomaly_reports
    add constraint unique_anomaly unique (ticker, trade_date, anomaly_type);

-- Remove unique constraint
ALTER TABLE anomaly_reports DROP CONSTRAINT unique_anomaly;

-- Optionally replace with a new constraint if you only want exact duplicates blocked:
CREATE UNIQUE INDEX unique_anomaly_idx 
ON anomaly_reports (ticker, trade_date, anomaly_type, description);