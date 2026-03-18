-- ============================================================
-- Superstore Financial Analysis – SQL Queries
-- Database: data/superstore.db   Table: sales
-- ============================================================


-- ── 1. REVENUE BY MONTH ─────────────────────────────────────
-- Monthly revenue trend to identify seasonality and growth
SELECT
    Year_Month,
    Year,
    Month,
    ROUND(SUM(Sales), 2)                          AS Total_Revenue,
    ROUND(SUM(Profit), 2)                         AS Total_Profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)   AS Profit_Margin_Pct
FROM sales
GROUP BY Year_Month, Year, Month
ORDER BY Year, Month;


-- ── 2. REVENUE & PROFIT BY CATEGORY ─────────────────────────
-- Identifies which category drives revenue vs. which is most profitable
SELECT
    Category,
    COUNT(*)                                       AS Order_Count,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)    AS Profit_Margin_Pct,
    ROUND(AVG(Sales), 2)                           AS Avg_Order_Value
FROM sales
GROUP BY Category
ORDER BY Total_Revenue DESC;


-- ── 3. REVENUE & PROFIT BY SUB-CATEGORY ─────────────────────
-- Drills into low-performing and high-performing sub-categories
SELECT
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)    AS Profit_Margin_Pct
FROM sales
GROUP BY Category, Sub_Category
ORDER BY Total_Profit DESC;


-- ── 4. REVENUE BY REGION ─────────────────────────────────────
-- Regional performance comparison
SELECT
    Region,
    COUNT(DISTINCT Order_ID)                       AS Total_Orders,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)    AS Profit_Margin_Pct
FROM sales
GROUP BY Region
ORDER BY Total_Revenue DESC;


-- ── 5. TOP 10 PERFORMING PRODUCTS ────────────────────────────
-- Highest-revenue products
SELECT
    Product_Name,
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit
FROM sales
GROUP BY Product_Name, Category, Sub_Category
ORDER BY Total_Revenue DESC
LIMIT 10;


-- ── 6. BOTTOM 10 PRODUCTS BY PROFIT ──────────────────────────
-- Loss-making or low-margin products (cost inefficiencies)
SELECT
    Product_Name,
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit
FROM sales
GROUP BY Product_Name, Category, Sub_Category
ORDER BY Total_Profit ASC
LIMIT 10;


-- ── 7. REVENUE BY CUSTOMER SEGMENT ───────────────────────────
SELECT
    Segment,
    COUNT(DISTINCT Customer_ID)                    AS Unique_Customers,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)    AS Profit_Margin_Pct
FROM sales
GROUP BY Segment
ORDER BY Total_Revenue DESC;


-- ── 8. QUARTERLY REVENUE GROWTH ──────────────────────────────
-- Quarter-over-quarter revenue for trend analysis
SELECT
    Year,
    Quarter,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit
FROM sales
GROUP BY Year, Quarter
ORDER BY Year, Quarter;


-- ── 9. PROFIT FLAG SUMMARY ───────────────────────────────────
-- How many orders are profitable vs. loss-making
SELECT
    Profit_Flag,
    COUNT(*)                                       AS Order_Count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales), 2) AS Pct_of_Total,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit
FROM sales
GROUP BY Profit_Flag;


-- ── 10. TOP 5 STATES BY REVENUE ──────────────────────────────
SELECT
    State,
    Region,
    ROUND(SUM(Sales), 2)                           AS Total_Revenue,
    ROUND(SUM(Profit), 2)                          AS Total_Profit
FROM sales
GROUP BY State, Region
ORDER BY Total_Revenue DESC
LIMIT 5;
