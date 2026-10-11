
-- =========================================================
-- SALES INTELLIGENCE HUB
-- 20 PREDEFINED SQL ANALYTICAL QUERIES
-- Database: sales_intelligence_hub
-- =========================================================

USE sales_intelligence_hub;

-- Q1. Retrieve all customer sales
SELECT *
FROM customer_sales
ORDER BY sale_id;

-- Q2. Retrieve all branches
SELECT *
FROM branches
ORDER BY branch_id;

-- Q3. Retrieve all payment splits
SELECT *
FROM payment_splits
ORDER BY payment_id;

-- Q4. Display all Open sales
SELECT *
FROM customer_sales
WHERE status = 'Open'
ORDER BY sale_id;

-- Q5. Retrieve Chennai branch sales
SELECT cs.*
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai'
ORDER BY cs.sale_id;

-- Q6. Calculate total gross sales
SELECT SUM(gross_sales) AS total_gross_sales
FROM customer_sales;

-- Q7. Calculate total received amount
SELECT SUM(received_amount) AS total_received_amount
FROM customer_sales;

-- Q8. Calculate total pending amount
SELECT SUM(pending_amount) AS total_pending_amount
FROM customer_sales;

-- Q9. Count sales per branch
SELECT
    b.branch_name,
    COUNT(cs.sale_id) AS total_sales
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY total_sales DESC;

-- Q10. Find average gross sales
SELECT AVG(gross_sales) AS average_gross_sales
FROM customer_sales;

-- Q11. Sales details with branch name
SELECT
    cs.sale_id,
    b.branch_name,
    cs.date,
    cs.name,
    cs.mobile_number,
    cs.product_name,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount,
    cs.status
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;

-- Q12. Sales details with branch and customer
SELECT
    b.branch_name,
    cs.sale_id,
    cs.name AS customer_name,
    cs.product_name,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;

-- Q13. Branch-wise total gross sales
SELECT
    b.branch_name,
    SUM(cs.gross_sales) AS total_gross_sales
FROM branches b
JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY total_gross_sales DESC;

-- Q14. Sales with payment method
SELECT
    cs.sale_id,
    cs.name AS customer_name,
    cs.product_name,
    ps.payment_method,
    ps.amount_paid,
    ps.payment_date
FROM customer_sales cs
JOIN payment_splits ps ON cs.sale_id = ps.sale_id
ORDER BY cs.sale_id, ps.payment_id;

-- Q15. Detailed sales payment information
SELECT
    cs.sale_id,
    b.branch_name,
    cs.name AS customer_name,
    cs.gross_sales,
    ps.payment_date,
    ps.amount_paid,
    ps.payment_method
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
JOIN payment_splits ps ON cs.sale_id = ps.sale_id
ORDER BY cs.sale_id, ps.payment_id;

-- Q16. Sales with pending amount greater than 5000
SELECT
    cs.sale_id,
    b.branch_name,
    cs.name AS customer_name,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE cs.pending_amount > 5000
ORDER BY cs.pending_amount DESC;

-- Q17. Top 3 highest gross sales
SELECT
    cs.sale_id,
    b.branch_name,
    cs.name AS customer_name,
    cs.product_name,
    cs.gross_sales
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.gross_sales DESC
LIMIT 3;

-- Q18. Branch with highest total gross sales
SELECT
    b.branch_name,
    SUM(cs.gross_sales) AS total_gross_sales
FROM branches b
JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY total_gross_sales DESC
LIMIT 1;

-- Q19. Monthly sales summary
SELECT
    YEAR(cs.date) AS sale_year,
    MONTH(cs.date) AS sale_month,
    SUM(cs.gross_sales) AS total_gross_sales,
    COUNT(cs.sale_id) AS total_sales
FROM customer_sales cs
GROUP BY YEAR(cs.date), MONTH(cs.date)
ORDER BY sale_year, sale_month;

-- Q20. Payment method-wise total collection
SELECT
    payment_method,
    SUM(amount_paid) AS total_collection
FROM payment_splits
GROUP BY payment_method
ORDER BY total_collection DESC;
