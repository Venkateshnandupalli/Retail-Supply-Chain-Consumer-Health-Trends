-- View 1: Daily Sales Trend by Category
CREATE VIEW vw_sales_trend AS
SELECT 
    "Order Date", 
    Category,
    SUM(Units_Sold) AS Total_Units_Sold,
    SUM(Revenue) AS Total_Revenue 
FROM retail_data
GROUP BY "Order Date", Category
ORDER BY "Order Date" ASC;