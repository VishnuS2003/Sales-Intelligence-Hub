# Database Setup Guide — Sales Intelligence Hub

## 1. Prerequisites

Install and configure:

- MySQL Server 8.0 or compatible version
- Python 3.13 or compatible version
- MySQL Workbench (recommended)
- The project files from this repository

## 2. Create the Database

Open MySQL Workbench and execute:

```sql
CREATE DATABASE IF NOT EXISTS sales_intelligence_hub;
USE sales_intelligence_hub;
```

## 3. Create the Database Tables and Trigger

Open `schema.sql` from the project repository, review it, and execute the script against the `sales_intelligence_hub` database.

The schema defines the four main tables:

- `branches`
- `customer_sales`
- `payment_splits`
- `users`

It also defines the trigger used to update received payment amounts and the generated column used to calculate pending amounts.

Confirm that the tables and trigger have been created successfully before importing data.

## 4. Import the CSV Datasets

The repository contains these files in the `data/` directory:

- `branches.csv`
- `customer_sales.csv`
- `payment_splits.csv`
- `users.csv`

Import the files into their corresponding tables using MySQL Workbench's Table Data Import Wizard or an equivalent CSV import process.

**Recommended import order:**

1. `branches.csv`
2. `customer_sales.csv`
3. `users.csv`
4. `payment_splits.csv`

The branch records must exist before importing records that reference branch IDs. Customer sales must exist before importing their payment splits.

Check the CSV column names and table structure before importing. Do not manually overwrite generated columns or trigger-maintained values. After importing the payment splits, verify the received and pending amounts.

## 5. Configure Database Credentials

Create a local `.env` file in the project directory alongside `app.py`.

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DB_NAME=sales_intelligence_hub
```

Replace the password placeholder with your own MySQL password.

**Security:** Never commit `.env` or publish database passwords. The repository's `.gitignore` should exclude `.env` and `.venv/`.

## 6. Install Python Dependencies

Open a terminal in the project directory, activate your virtual environment if applicable, and run:

```bash
python -m pip install -r requirements.txt
```

## 7. Run the Streamlit Application

From the project directory, run:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

Log in using an account configured in the `users` table.

## 8. Verify the Database

Run the following checks in MySQL Workbench:

```sql
USE sales_intelligence_hub;

SELECT COUNT(*) AS total_branches FROM branches;
SELECT COUNT(*) AS total_sales FROM customer_sales;
SELECT COUNT(*) AS total_users FROM users;
SELECT COUNT(*) AS total_payments FROM payment_splits;

SELECT
    SUM(gross_sales) AS total_gross_sales,
    SUM(received_amount) AS total_received,
    SUM(pending_amount) AS total_pending
FROM customer_sales;
```

For the supplied GUVI dataset, the expected record counts are:

- Branches: 8
- Customer sales: 1,000
- Users: 9
- Payment splits: 2,011

The totals should reconcile so that gross sales minus received amounts equals pending amounts.

## 9. SQL Analytics

The file `queries.sql` contains 20 predefined analytical queries covering sales retrieval, aggregations, branch performance, joins, pending balances, monthly trends, and payment-method collections.

Execute the queries after the database tables have been created and the data has been imported.

## 10. Troubleshooting

- **Database connection error:** Verify that MySQL is running and the `.env` values are correct.
- **Missing Python package:** Run `python -m pip install -r requirements.txt`.
- **Foreign-key import error:** Check the import order and confirm referenced branch and sale IDs exist.
- **Incorrect received amounts:** Verify that the trigger exists and that payment splits were imported correctly.
- **Missing table or column:** Review `schema.sql` and confirm that the correct database is selected.
