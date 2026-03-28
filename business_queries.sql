-- PhonePe Transaction Insights
-- Reusable SQL queries for key business questions

-- 1. Yearly transaction growth across India
SELECT
    Year,
    SUM(Transaction_Count) AS total_transaction_count,
    ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS total_transaction_amount_trillion
FROM aggregated_transaction_country
GROUP BY Year
ORDER BY Year;

-- 2. Top states by transaction value
SELECT
    State,
    ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion,
    ROUND(SUM(Transaction_Count) / 1000000000.0, 2) AS transaction_count_billion
FROM aggregated_transaction_state
GROUP BY State
ORDER BY transaction_amount_trillion DESC
LIMIT 10;

-- 3. Payment category performance
SELECT
    Transaction_Type,
    ROUND(SUM(Transaction_Count) / 1000000000.0, 2) AS transaction_count_billion,
    ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion
FROM aggregated_transaction_state
GROUP BY Transaction_Type
ORDER BY transaction_amount_trillion DESC;

-- 4. Latest user engagement snapshot by state
WITH latest_user_period AS (
    SELECT Year, MAX(Quarter) AS Quarter
    FROM aggregated_user_state
    WHERE Year = (SELECT MAX(Year) FROM aggregated_user_state)
)
SELECT
    a.State,
    a.Year,
    a.Quarter,
    a.Registered_Users,
    a.App_Opens
FROM aggregated_user_state AS a
JOIN latest_user_period AS l
    ON a.Year = l.Year AND a.Quarter = l.Quarter
ORDER BY a.Registered_Users DESC;

-- 5. Insurance performance by state
SELECT
    State,
    SUM(Transaction_Count) AS insurance_transaction_count,
    ROUND(SUM(Transaction_Amount) / 10000000.0, 2) AS insurance_amount_crore
FROM aggregated_insurance_state
GROUP BY State
ORDER BY insurance_amount_crore DESC
LIMIT 10;

-- 6. Top transaction states, districts, and pincodes
SELECT
    Type,
    Entity_Name,
    SUM(Transaction_Count) AS total_transaction_count,
    ROUND(SUM(Transaction_Amount) / 1000000000.0, 2) AS total_transaction_amount_billion
FROM top_transaction
GROUP BY Type, Entity_Name
ORDER BY Type, total_transaction_amount_billion DESC;
