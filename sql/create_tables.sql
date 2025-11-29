CREATE DATABASE IF NOT EXISTS walmart;

CREATE TABLE IF NOT EXISTS walmart.weekly_sales (
    store           UInt16,
    week_date       Date,
    weekly_sales    Float64,
    holiday_flag    UInt8,
    temperature     Float32,
    fuel_price      Float32,
    cpi             Float32,
    unemployment    Float32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(week_date)
ORDER BY (store, week_date);
