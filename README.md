# Sales Intelligence Hub

## Project Overview

Sales Intelligence Hub is a branch-based sales management and financial analytics application developed using Python, MySQL, and Streamlit.

It helps monitor sales performance, customer payments, pending balances, branch performance, and payment collections.

## Objectives

- Track sales across multiple branches.
- Monitor gross sales, received payments, and pending amounts.
- Support split payments for individual sales.
- Automate received and pending amount calculations.
- Provide role-based access for Super Admin and branch Admin users.
- Analyze sales performance through an interactive dashboard.

## Technology Stack

- **Python** — application logic
- **MySQL** — relational database
- **Streamlit** — interactive web dashboard
- **SQL** — data retrieval, joins, aggregations, and analytics
- **MySQL triggers and generated columns** — payment calculations

## Database Design

The database contains four main tables:

1. `branches` — branch and administrator details.
2. `customer_sales` — customer sales transactions.
3. `payment_splits` — individual payment records.
4. `users` — login accounts and user roles.

The `update_received_amount` trigger updates the received amount when a payment record is inserted. The generated `pending_amount` column calculates the outstanding balance.

## Dashboard Features

- Login and role-based access
- Add new sales
- Record split payments
- Filter sales by branch, product, and date
- View gross sales, received amounts, and pending balances
- Branch-wise and product-wise analytics
- Payment method analysis
- Monthly sales trends
- Predefined SQL Query Engine

## Setup

### Prerequisites

- Python
- MySQL Server
- MySQL database `sales_intelligence_hub`

### Configuration

Create a `.env` file in the project directory with your local database settings:

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DB_NAME=sales_intelligence_hub
```

Replace the password placeholder with your own MySQL password. **Never commit `.env` to GitHub.**

Install the required Python packages in your virtual environment. The application uses Streamlit, MySQL Connector/Python, pandas, and python-dotenv.

Run the application:

```bash
streamlit run app.py
```

## Testing

The application was tested locally with the supplied dataset of 1,000 sales records across 8 branches and 2,011 payment records.

Super Admin login, branch-restricted Admin access, dashboard analytics, and the SQL Query Engine were verified.

## Security Note

Keep database credentials private. Use environment variables for local configuration and never publish passwords or sensitive credentials in source files.

## Project Status

The application and database schema have been implemented and tested locally. Database setup and configuration are required before running it in another environment.
