-- Когорты по дате первого события пользователя и retention по дням

WITH first_seen AS (
    SELECT
        user_id,
        min(event_date) AS cohort_date
    FROM apptrack.events
    GROUP BY user_id
),

activity AS (
    SELECT
        e.user_id,
        e.event_date,
        fs.cohort_date,
        dateDiff('day', fs.cohort_date, e.event_date) AS days_since_cohort
    FROM apptrack.events e
    INNER JOIN first_seen fs USING (user_id)
)

SELECT
    cohort_date,
    days_since_cohort,
    uniqExact(user_id)                                        AS active_users,
    uniqExactIf(user_id, days_since_cohort = 0)               AS cohort_size,
    active_users / max(cohort_size) OVER (PARTITION BY cohort_date) AS retention
FROM activity
WHERE days_since_cohort BETWEEN 0 AND 30
GROUP BY
    cohort_date,
    days_since_cohort
ORDER BY
    cohort_date,
    days_since_cohort;
