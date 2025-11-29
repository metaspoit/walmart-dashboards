-- Влияние праздничных недель на продажи по магазинам

SELECT
    store,
    holiday_flag,
    avg(weekly_sales) AS avg_weekly_sales
FROM walmart.weekly_sales
GROUP BY
    store,
    holiday_flag
ORDER BY
    store,
    holiday_flag;
