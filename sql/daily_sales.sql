SELECT
    week_date,
    store,
    sum(weekly_sales)               AS weekly_sales_total,
    avg(weekly_sales)               AS weekly_sales_avg,
    max(weekly_sales)               AS weekly_sales_max,
    sumIf(weekly_sales, holiday_flag = 1) AS holiday_sales,
    sumIf(weekly_sales, holiday_flag = 0) AS non_holiday_sales
FROM walmart.weekly_sales
GROUP BY
    week_date,
    store
ORDER BY
    week_date,
    store
LIMIT 100;
