
create table spac_list (
    ticker text primary key,
    company_name text,
    ipo_date date,
    exchange text,
    country text
);

-- Store daily OHLCV data
create table spac_data (
    id bigserial primary key,
    ticker text references spac_list(ticker),
    trade_date date not null,
    open numeric,
    high numeric,
    low numeric,
    close numeric,
    volume bigint,
    created_at timestamp default now()
);

create extension if not exists vector;

-- Store anomaly events
create table anomaly_reports (
    id bigserial primary key,
    ticker text references spac_list(ticker),
    trade_date date,
    anomaly_type text,
    description text,
    embedding vector(1536), -- pgvector for RAG
    created_at timestamp default now()
);

-- Store alert history
create table alerts_log (
    id bigserial primary key,
    alert_date date not null,
    alert_channel text, -- "discord", "email"
    message text,
    created_at timestamp default now()
);