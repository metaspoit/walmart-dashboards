-- Рейтинг магазинов по средним и суммарным продажам за весь период

SELECT
    store,
    avg(weekly_sales) AS avg_weekly_sales,
    sum(weekly_sales) AS total_sales
FROM walmart.weekly_sales
GROUP BY store
ORDER BY avg_weekly_sales DESC;
