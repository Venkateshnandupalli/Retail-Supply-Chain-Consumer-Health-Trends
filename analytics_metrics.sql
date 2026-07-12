-- View 1: Daily Sales Trend by Category
DROP VIEW IF EXISTS vw_sales_trend;
CREATE VIEW vw_sales_trend AS
SELECT 
    Date, 
    Category,
    SUM(Units_Sold) AS Total_Units_Sold,
    SUM(Units_Sold * Unit_Price) AS Total_Revenue 
FROM retail_data
GROUP BY Date, Category
ORDER BY Date ASC;