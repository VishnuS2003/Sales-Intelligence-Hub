SHOW DATABASES;
CREATE DATABASE sales_intelligence_hub;
SHOW DATABASES;

USE sales_intelligence_hub;

SELECT DATABASE();
SHOW TABLES;

CREATE TABLE branches (
    branch_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_name VARCHAR(100),
    branch_admin_name VARCHAR(100)
);

SHOW TABLES;


CREATE TABLE customer_sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_id INT,
    date DATE,
    name VARCHAR(100),
    mobile_number VARCHAR(15),
    product_name ENUM('DS', 'DA', 'BA', 'FSD'),
    gross_sales DECIMAL(10,2),
    received_amount DECIMAL(10,2),
    pending_amount DECIMAL(10,2)
        GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status ENUM('Open','Close'),

    UNIQUE (mobile_number),

    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);

DESCRIBE customer_sales;

SHOW CREATE TABLE customer_sales;

USE sales_intelligence_hub;

CREATE TABLE payment_splits (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT,
    payment_date DATE,
    amount_paid DECIMAL(10,2),
    payment_method ENUM('Cash','UPI','Card'),

    FOREIGN KEY (sale_id)
        REFERENCES customer_sales(sale_id)
);

DESCRIBE payment_splits;


CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100),
    password VARCHAR(255),
    branch_id INT,
    role ENUM('Super Admin','Admin'),
    email VARCHAR(255),

    UNIQUE (email),

    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);


DESCRIBE users;


INSERT INTO branches (branch_name, branch_admin_name)
VALUES
('Chennai', 'Arun'),
('Bangalore', 'Priya'),
('Hyderabad', 'Rahul');

SELECT * FROM branches;


INSERT INTO customer_sales
(branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
VALUES
(1, '2026-10-01', 'Karthik', '9876500001', 'DS', 50000.00, 0.00, 'Open'),
(1, '2026-10-01', 'Meena',   '9876500002', 'DA', 35000.00, 0.00, 'Open'),
(2, '2026-10-02', 'Rahul',   '9876500003', 'FSD', 75000.00, 0.00, 'Open'),
(2, '2026-10-02', 'Divya',   '9876500004', 'BA', 45000.00, 0.00, 'Open'),
(3, '2026-10-02', 'Suresh',  '9876500005', 'DS', 60000.00, 0.00, 'Open');

SELECT * FROM customer_sales;


DELIMITER //

CREATE TRIGGER update_received_amount
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = (
        SELECT COALESCE(SUM(amount_paid), 0)
        FROM payment_splits
        WHERE sale_id = NEW.sale_id
    )
    WHERE sale_id = NEW.sale_id;
END //

DELIMITER ;


INSERT INTO payment_splits
(sale_id, payment_date, amount_paid, payment_method)
VALUES
(1, '2026-10-02', 20000.00, 'UPI');


SELECT
    sale_id,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE sale_id = 1;

INSERT INTO payment_splits
(sale_id, payment_date, amount_paid, payment_method)
VALUES
(1, '2026-10-02', 10000.00, 'Cash');


SELECT
    sale_id,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE sale_id = 1;

SHOW TABLES;

SELECT * FROM payment_splits;

SELECT
    sale_id,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE sale_id = 1;

SELECT *
FROM customer_sales;

SELECT *
FROM branches;

SELECT *
FROM payment_splits;

SELECT *
FROM customer_sales
WHERE status = 'Open';

show tables

SELECT cs.*
FROM customer_sales AS cs
JOIN branches AS b
    ON cs.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai';

select * from customer_sales;


SELECT SUM(gross_sales)
FROM customer_sales;

SELECT SUM(received_amount)
FROM customer_sales;

SELECT SUM(pending_amount)
FROM customer_sales;

SELECT branch_id, COUNT(sale_id)
FROM customer_sales
GROUP BY branch_id;

SELECT AVG(gross_sales)
FROM CUSTOMER_sales;


SELECT
    cs.sale_id,
    cs.date,
    cs.name,
    cs.product_name,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount,
    cs.status,
    b.branch_name
FROM customer_sales AS cs
JOIN branches AS b
    ON cs.branch_id = b.branch_id;
    
    SELECT
    b.branch_name,
    cs.name AS customer_name,
    cs.product_name,
    cs.gross_sales,
    cs.status
FROM customer_sales AS cs
JOIN branches AS b
    ON cs.branch_id = b.branch_id;
    
    
    SELECT
    b.branch_name,
    SUM(cs.gross_sales) AS total_gross_sales
FROM customer_sales AS cs
JOIN branches AS b
    ON cs.branch_id = b.branch_id
GROUP BY b.branch_name;


SELECT
    cs.sale_id,
    cs.name AS customer_name,
    cs.product_name,
    ps.amount_paid,
    ps.payment_method
FROM customer_sales AS cs
JOIN payment_splits AS ps
    ON cs.sale_id = ps.sale_id;
    
    
    SELECT
    cs.sale_id,
    cs.name AS customer_name,
    cs.gross_sales,
    cs.received_amount,
    ps.payment_date,
    ps.amount_paid,
    ps.payment_method
FROM customer_sales AS cs
JOIN payment_splits AS ps
    ON cs.sale_id = ps.sale_id;
    
    SELECT *
FROM customer_sales
WHERE pending_amount > 5000;


SELECT *
FROM customer_sales
ORDER BY gross_sales DESC
LIMIT 3;


SELECT
    b.branch_name,
    SUM(cs.gross_sales) AS total_gross_sales
FROM customer_sales AS cs
JOIN branches AS b
    ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_gross_sales DESC
LIMIT 1;


SELECT
    YEAR(date) AS sales_year,
    MONTH(date) AS sales_month,
    SUM(gross_sales) AS total_sales
FROM customer_sales
GROUP BY YEAR(date), MONTH(date)
ORDER BY sales_year, sales_month;

SELECT
    payment_method,
    SUM(amount_paid) AS total_collection
FROM payment_splits
GROUP BY payment_method;