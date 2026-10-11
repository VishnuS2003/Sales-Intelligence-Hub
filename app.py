import os

import streamlit as st

import mysql.connector

from mysql.connector import Error

import pandas as pd

from dotenv import load_dotenv

load_dotenv()

# =========================================================

# DATABASE CONNECTION

# =========================================================

def get_connection():

    return mysql.connector.connect(

        host=os.getenv("DB_HOST", "localhost"),

        user=os.getenv("DB_USER", "root"),

        password=os.getenv("DB_PASSWORD"),

        database=os.getenv("DB_NAME", "sales_intelligence_hub")

    )

# =========================================================

# CONSTANTS

# =========================================================

PRODUCTS = ["DS", "DA", "BA", "FSD", "ML", "AI", "BI", "SQL"]

PAYMENT_METHODS = ["Cash", "UPI", "Card"]

# =========================================================

# PAGE CONFIG

# =========================================================

st.set_page_config(

    page_title="Sales Intelligence Hub",

    page_icon="📊",

    layout="wide"

)

# =========================================================

# SESSION STATE

# =========================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

if "username" not in st.session_state:

    st.session_state.username = None

if "role" not in st.session_state:

    st.session_state.role = None

if "branch_id" not in st.session_state:

    st.session_state.branch_id = None

# =========================================================

# LOGIN

# =========================================================

if not st.session_state.logged_in:

    st.title("📊 Sales Intelligence Hub")

    st.subheader("Login")

    username = st.text_input("Username")

    password = st.text_input("Password", type="password")

    if st.button("Login"):

        try:

            conn = get_connection()

            cursor = conn.cursor(dictionary=True)

            cursor.execute("""

                SELECT

                    user_id,

                    username,

                    password,

                    branch_id,

                    role

                FROM users

                WHERE username = %s

            """, (username,))

            user = cursor.fetchone()

            cursor.close()

            conn.close()

            if user and user["password"] == password:

                st.session_state.logged_in = True

                st.session_state.username = user["username"]

                st.session_state.role = user["role"]

                st.session_state.branch_id = user["branch_id"]

                st.success("Login successful!")

                st.rerun()

            else:

                st.error("Invalid username or password.")

        except Error as e:

            st.error(f"Database error: {e}")

    st.stop()

# =========================================================

# SIDEBAR

# =========================================================

st.sidebar.title("📊 Sales Intelligence Hub")

st.sidebar.write(f"👤 **User:** {st.session_state.username}")

st.sidebar.write(f"🔐 **Role:** {st.session_state.role}")

if st.session_state.role == "Admin":

    st.sidebar.write(

        f"🏢 **Branch ID:** {st.session_state.branch_id}"

    )

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False

    st.session_state.username = None

    st.session_state.role = None

    st.session_state.branch_id = None

    st.rerun()

# =========================================================

# DATABASE CONNECTION

# =========================================================

try:

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

except Error as e:

    st.error(f"Database connection failed: {e}")

    st.stop()

# =========================================================

# MAIN TITLE

# =========================================================

st.title("📊 Sales Intelligence Dashboard")

st.write(f"Welcome **{st.session_state.username}**!")

# =========================================================

# GET BRANCHES

# =========================================================

cursor.execute("""

    SELECT branch_id, branch_name

    FROM branches

    ORDER BY branch_id

""")

branches = cursor.fetchall()

# =========================================================

# ADD NEW SALE

# =========================================================

st.subheader("➕ Add New Sale")

with st.form("add_sale_form"):

    sale_date = st.date_input("Sale Date")

    customer_name = st.text_input("Customer Name")

    mobile_number = st.text_input("Mobile Number")

    product_name = st.selectbox(

        "Product",

        PRODUCTS

    )

    gross_sales = st.number_input(

        "Gross Sales",

        min_value=0.0,

        step=1000.0

    )

    if st.session_state.role == "Super Admin":

        branch_options = {

            branch["branch_name"]: branch["branch_id"]

            for branch in branches

        }

        selected_branch_name_for_sale = st.selectbox(

            "Branch",

            list(branch_options.keys())

        )

        selected_branch_id_for_sale = branch_options[

            selected_branch_name_for_sale

        ]

    else:

        selected_branch_id_for_sale = st.session_state.branch_id

        selected_branch_name_for_sale = next(

            (

                branch["branch_name"]

                for branch in branches

                if branch["branch_id"]

                == selected_branch_id_for_sale

            ),

            "Unknown"

        )

        st.info(

            f"Admin access restricted to: "

            f"{selected_branch_name_for_sale}"

        )

    submit_sale = st.form_submit_button("Add Sale")

    if submit_sale:

        if not customer_name or not mobile_number:

            st.error(

                "Customer name and mobile number are required."

            )

        elif gross_sales <= 0:

            st.error(

                "Gross sales must be greater than 0."

            )

        else:

            try:

                cursor.execute("""

                    INSERT INTO customer_sales

                    (

                        branch_id,

                        date,

                        name,

                        mobile_number,

                        product_name,

                        gross_sales,

                        received_amount,

                        status

                    )

                    VALUES

                    (%s, %s, %s, %s, %s, %s, %s, %s)

                """, (

                    selected_branch_id_for_sale,

                    sale_date,

                    customer_name,

                    mobile_number,

                    product_name,

                    gross_sales,

                    0.00,

                    "Open"

                ))

                conn.commit()

                st.success(

                    f"Sale added successfully to "

                    f"{selected_branch_name_for_sale}!"

                )

            except Error as e:

                conn.rollback()

                st.error(f"Unable to add sale: {e}")

# =========================================================

# ADD PAYMENT SPLIT

# =========================================================

st.divider()

st.subheader("💰 Add Payment Split")

if st.session_state.role == "Super Admin":

    cursor.execute("""

        SELECT

            cs.sale_id,

            cs.name,

            cs.product_name,

            cs.gross_sales,

            cs.received_amount,

            cs.pending_amount,

            b.branch_name

        FROM customer_sales cs

        JOIN branches b

            ON cs.branch_id = b.branch_id

        WHERE cs.pending_amount > 0

        ORDER BY cs.sale_id

    """)

else:

    cursor.execute("""

        SELECT

            cs.sale_id,

            cs.name,

            cs.product_name,

            cs.gross_sales,

            cs.received_amount,

            cs.pending_amount,

            b.branch_name

        FROM customer_sales cs

        JOIN branches b

            ON cs.branch_id = b.branch_id

        WHERE cs.branch_id = %s

          AND cs.pending_amount > 0

        ORDER BY cs.sale_id

    """, (st.session_state.branch_id,))

payment_sales = cursor.fetchall()

if payment_sales:

    sale_options = {}

    for sale in payment_sales:

        label = (

            f"Sale #{sale['sale_id']} | "

            f"{sale['name']} | "

            f"{sale['product_name']} | "

            f"{sale['branch_name']} | "

            f"Pending ₹{float(sale['pending_amount']):,.2f}"

        )

        sale_options[label] = sale

    with st.form("payment_form"):

        selected_sale_label = st.selectbox(

            "Select Sale",

            list(sale_options.keys())

        )

        selected_sale = sale_options[selected_sale_label]

        st.write(

            f"**Gross Sales:** "

            f"₹{float(selected_sale['gross_sales']):,.2f}"

        )

        st.write(

            f"**Already Received:** "

            f"₹{float(selected_sale['received_amount']):,.2f}"

        )

        st.write(

            f"**Pending:** "

            f"₹{float(selected_sale['pending_amount']):,.2f}"

        )

        payment_date = st.date_input("Payment Date")

        amount_paid = st.number_input(

            "Amount Paid",

            min_value=0.0,

            max_value=float(selected_sale["pending_amount"]),

            step=1000.0

        )

        payment_method = st.selectbox(

            "Payment Method",

            PAYMENT_METHODS

        )

        submit_payment = st.form_submit_button("Add Payment")

        if submit_payment:

            if amount_paid <= 0:

                st.error(

                    "Payment amount must be greater than 0."

                )

            else:

                try:

                    cursor.execute("""

                        INSERT INTO payment_splits

                        (

                            sale_id,

                            payment_date,

                            amount_paid,

                            payment_method

                        )

                        VALUES

                        (%s, %s, %s, %s)

                    """, (

                        selected_sale["sale_id"],

                        payment_date,

                        amount_paid,

                        payment_method

                    ))

                    conn.commit()

                    st.success(

                        "Payment added successfully!"

                    )

                    st.info(

                        "MySQL trigger updated the "

                        "received amount automatically."

                    )

                    st.rerun()

                except Error as e:

                    conn.rollback()

                    st.error(f"Unable to add payment: {e}")

else:

    st.success(

        "No pending payments are available."

    )

# =========================================================

# FILTERS

# =========================================================

st.divider()

st.subheader("🔎 Sales Filters")

col1, col2, col3 = st.columns(3)

with col1:

    if st.session_state.role == "Super Admin":

        branch_filter_options = ["All"]

        branch_filter_options.extend(

            [branch["branch_name"] for branch in branches]

        )

        selected_branch = st.selectbox(

            "Branch Name",

            branch_filter_options

        )

    else:

        selected_branch = next(

            (

                branch["branch_name"]

                for branch in branches

                if branch["branch_id"]

                == st.session_state.branch_id

            ),

            "Unknown"

        )

        st.selectbox(

            "Branch Name",

            [selected_branch],

            disabled=True

        )

with col2:

    selected_product = st.selectbox(

        "Product Name",

        ["All Products"] + PRODUCTS

    )

with col3:

    use_date_filter = st.checkbox("Filter by Date")

start_date = None

end_date = None

if use_date_filter:

    date_col1, date_col2 = st.columns(2)

    with date_col1:

        start_date = st.date_input("Start Date")

    with date_col2:

        end_date = st.date_input("End Date")

# =========================================================

# BUILD FILTER CONDITIONS

# =========================================================

conditions = []

params = []

if st.session_state.role == "Admin":

    conditions.append("cs.branch_id = %s")

    params.append(st.session_state.branch_id)

if (

    st.session_state.role == "Super Admin"

    and selected_branch != "All"

):

    conditions.append("b.branch_name = %s")

    params.append(selected_branch)

if selected_product != "All Products":

    conditions.append("cs.product_name = %s")

    params.append(selected_product)

if use_date_filter:

    conditions.append("cs.date BETWEEN %s AND %s")

    params.extend([start_date, end_date])

where_clause = ""

if conditions:

    where_clause = "WHERE " + " AND ".join(conditions)

# =========================================================

# KPI

# =========================================================

kpi_query = f"""

    SELECT

        COALESCE(SUM(cs.gross_sales), 0) AS total_sales,

        COALESCE(SUM(cs.received_amount), 0) AS total_received,

        COALESCE(SUM(cs.pending_amount), 0) AS total_pending

    FROM customer_sales cs

    JOIN branches b

        ON cs.branch_id = b.branch_id

    {where_clause}

"""

cursor.execute(kpi_query, tuple(params))

kpis = cursor.fetchone()

st.subheader("📌 Financial Overview")

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:

    st.metric(

        "💰 Total Sales",

        f"₹{float(kpis['total_sales']):,.2f}"

    )

with kpi2:

    st.metric(

        "💵 Total Received",

        f"₹{float(kpis['total_received']):,.2f}"

    )

with kpi3:

    st.metric(

        "⏳ Total Pending",

        f"₹{float(kpis['total_pending']):,.2f}"

    )

if float(kpis["total_sales"]) > 0:

    pending_percentage = (

        float(kpis["total_pending"])

        / float(kpis["total_sales"])

    ) * 100

    st.write(

        f"**Pending Collection:** "

        f"{pending_percentage:.2f}%"

    )

# =========================================================

# SALES RECORDS

# =========================================================

st.subheader("📋 Sales Records")

sales_query = f"""

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

    JOIN branches b

        ON cs.branch_id = b.branch_id

    {where_clause}

    ORDER BY cs.sale_id DESC

"""

cursor.execute(sales_query, tuple(params))

sales = cursor.fetchall()

if sales:

    sales_df = pd.DataFrame(sales)

    st.dataframe(

        sales_df,

        use_container_width=True

    )

else:

    st.info(

        "No sales records match the selected filters."

    )

# =========================================================

# REPORTS & ANALYTICS

# =========================================================

st.divider()

st.header("📈 Reports & Analytics")

# =========================================================

# BRANCH PERFORMANCE

# =========================================================

st.subheader("🏢 Branch-wise Sales Performance")

branch_query = f"""

    SELECT

        b.branch_name AS Branch,

        SUM(cs.gross_sales) AS Total_Sales,

        SUM(cs.received_amount) AS Received,

        SUM(cs.pending_amount) AS Pending,

        COUNT(cs.sale_id) AS Number_of_Sales

    FROM customer_sales cs

    JOIN branches b

        ON cs.branch_id = b.branch_id

    {where_clause}

    GROUP BY b.branch_id, b.branch_name

    ORDER BY Total_Sales DESC

"""

cursor.execute(branch_query, tuple(params))

branch_data = cursor.fetchall()

if branch_data:

    branch_df = pd.DataFrame(branch_data)

    for column in ["Total_Sales", "Received", "Pending"]:

        branch_df[column] = branch_df[column].astype(float)

    st.dataframe(

        branch_df,

        use_container_width=True

    )

    st.bar_chart(

        branch_df.set_index("Branch")[["Total_Sales"]]

    )

# =========================================================

# RECEIVED VS PENDING

# =========================================================

st.subheader("💰 Received vs Pending")

received_pending_df = pd.DataFrame({

    "Amount": [

        float(kpis["total_received"]),

        float(kpis["total_pending"])

    ]

}, index=["Received", "Pending"])

st.bar_chart(received_pending_df)

# =========================================================

# PAYMENT METHOD ANALYSIS

# =========================================================

st.subheader("💳 Payment Method Analysis")

payment_query = f"""

    SELECT

        ps.payment_method AS Payment_Method,

        SUM(ps.amount_paid) AS Total_Collected

    FROM payment_splits ps

    JOIN customer_sales cs

        ON ps.sale_id = cs.sale_id

    JOIN branches b

        ON cs.branch_id = b.branch_id

    {where_clause}

    GROUP BY ps.payment_method

    ORDER BY Total_Collected DESC

"""

cursor.execute(payment_query, tuple(params))

payment_data = cursor.fetchall()

if payment_data:

    payment_df = pd.DataFrame(payment_data)

    payment_df["Total_Collected"] = (

        payment_df["Total_Collected"].astype(float)

    )

    st.dataframe(

        payment_df,

        use_container_width=True

    )

    st.bar_chart(

        payment_df.set_index("Payment_Method")

    )

else:

    st.info(

        "No payment data available for the selected filters."

    )

# =========================================================

# SALES TREND

# =========================================================

st.subheader("📅 Sales Trend")

trend_query = f"""

    SELECT

        cs.date AS Sale_Date,

        SUM(cs.gross_sales) AS Total_Sales

    FROM customer_sales cs

    JOIN branches b

        ON cs.branch_id = b.branch_id

    {where_clause}

    GROUP BY cs.date

    ORDER BY cs.date

"""

cursor.execute(trend_query, tuple(params))

trend_data = cursor.fetchall()

if trend_data:

    trend_df = pd.DataFrame(trend_data)

    trend_df["Sale_Date"] = pd.to_datetime(

        trend_df["Sale_Date"]

    )

    trend_df["Total_Sales"] = (

        trend_df["Total_Sales"].astype(float)

    )

    trend_df = trend_df.set_index("Sale_Date")

    st.line_chart(

        trend_df["Total_Sales"]

    )

else:

    st.info("No sales trend data available.")

# =========================================================

# PRODUCT PERFORMANCE

# =========================================================

st.subheader("📦 Product Performance")

product_query = f"""

    SELECT

        cs.product_name AS Product,

        COUNT(cs.sale_id) AS Number_of_Sales,

        SUM(cs.gross_sales) AS Total_Sales

    FROM customer_sales cs

    JOIN branches b

        ON cs.branch_id = b.branch_id

    {where_clause}

    GROUP BY cs.product_name

    ORDER BY Total_Sales DESC

"""

cursor.execute(product_query, tuple(params))

product_data = cursor.fetchall()

if product_data:

    product_df = pd.DataFrame(product_data)

    product_df["Total_Sales"] = (

        product_df["Total_Sales"].astype(float)

    )

    st.dataframe(

        product_df,

        use_container_width=True

    )

    st.bar_chart(

        product_df.set_index("Product")[["Total_Sales"]]

    )

# =========================================================

# SQL QUERY ENGINE

# =========================================================

st.divider()

st.header("🧮 SQL Query Engine")

st.write(

    "Run the predefined SQL analytical queries required by the project."

)

sql_queries = {

    "Q1 — Retrieve all customer sales": """

        SELECT *

        FROM customer_sales

        ORDER BY sale_id;

    """,

    "Q2 — Retrieve all branches": """

        SELECT *

        FROM branches

        ORDER BY branch_id;

    """,

    "Q3 — Retrieve all payment splits": """

        SELECT *

        FROM payment_splits

        ORDER BY payment_id;

    """,

    "Q4 — Display all Open sales": """

        SELECT *

        FROM customer_sales

        WHERE status = 'Open'

        ORDER BY sale_id;

    """,

    "Q5 — Retrieve Chennai branch sales": """
        SELECT cs.*
        FROM customer_sales cs
        JOIN branches b ON cs.branch_id = b.branch_id
        WHERE b.branch_name = 'Chennai'
        ORDER BY cs.sale_id;
    """,

    "Q6 — Calculate total gross sales": """

        SELECT

            SUM(gross_sales) AS total_gross_sales

        FROM customer_sales;

    """,

    "Q7 — Calculate total received amount": """

        SELECT

            SUM(received_amount) AS total_received_amount

        FROM customer_sales;

    """,

    "Q8 — Calculate total pending amount": """

        SELECT

            SUM(pending_amount) AS total_pending_amount

        FROM customer_sales;

    """,

    "Q9 — Count sales per branch": """

        SELECT

            b.branch_name,

            COUNT(cs.sale_id) AS total_sales

        FROM branches b

        LEFT JOIN customer_sales cs

            ON b.branch_id = cs.branch_id

        GROUP BY b.branch_id, b.branch_name

        ORDER BY total_sales DESC;

    """,

    "Q10 — Find average gross sales": """

        SELECT

            AVG(gross_sales) AS average_gross_sales

        FROM customer_sales;

    """,

    "Q11 — Sales details with branch name": """

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

        JOIN branches b

            ON cs.branch_id = b.branch_id

        ORDER BY cs.sale_id;

    """,

    "Q12 — Sales details with branch and customer": """

        SELECT

            b.branch_name,

            cs.sale_id,

            cs.name AS customer_name,

            cs.product_name,

            cs.gross_sales,

            cs.received_amount,

            cs.pending_amount

        FROM customer_sales cs

        JOIN branches b

            ON cs.branch_id = b.branch_id

        ORDER BY cs.sale_id;

    """,

    "Q13 — Branch-wise total gross sales": """

        SELECT

            b.branch_name,

            SUM(cs.gross_sales) AS total_gross_sales

        FROM branches b

        JOIN customer_sales cs

            ON b.branch_id = cs.branch_id

        GROUP BY b.branch_id, b.branch_name

        ORDER BY total_gross_sales DESC;

    """,

    "Q14 — Sales with payment method": """

        SELECT

            cs.sale_id,

            cs.name AS customer_name,

            cs.product_name,

            ps.payment_method,

            ps.amount_paid,

            ps.payment_date

        FROM customer_sales cs

        JOIN payment_splits ps

            ON cs.sale_id = ps.sale_id

        ORDER BY cs.sale_id, ps.payment_id;

    """,

    "Q15 — Detailed sales payment information": """

        SELECT

            cs.sale_id,

            b.branch_name,

            cs.name AS customer_name,

            cs.gross_sales,

            ps.payment_date,

            ps.amount_paid,

            ps.payment_method

        FROM customer_sales cs

        JOIN branches b

            ON cs.branch_id = b.branch_id

        JOIN payment_splits ps

            ON cs.sale_id = ps.sale_id

        ORDER BY cs.sale_id, ps.payment_id;

    """,

    "Q16 — Sales with pending amount greater than 5000": """

        SELECT

            cs.sale_id,

            b.branch_name,

            cs.name AS customer_name,

            cs.gross_sales,

            cs.received_amount,

            cs.pending_amount

        FROM customer_sales cs

        JOIN branches b

            ON cs.branch_id = b.branch_id

        WHERE cs.pending_amount > 5000

        ORDER BY cs.pending_amount DESC;

    """,

    "Q17 — Top 3 highest gross sales": """

        SELECT

            cs.sale_id,

            b.branch_name,

            cs.name AS customer_name,

            cs.product_name,

            cs.gross_sales

        FROM customer_sales cs

        JOIN branches b

            ON cs.branch_id = b.branch_id

        ORDER BY cs.gross_sales DESC

        LIMIT 3;

    """,

    "Q18 — Branch with highest total gross sales": """

        SELECT

            b.branch_name,

            SUM(cs.gross_sales) AS total_gross_sales

        FROM branches b

        JOIN customer_sales cs

            ON b.branch_id = cs.branch_id

        GROUP BY b.branch_id, b.branch_name

        ORDER BY total_gross_sales DESC

        LIMIT 1;

    """,

    "Q19 — Monthly sales summary": """

        SELECT

            YEAR(cs.date) AS sale_year,

            MONTH(cs.date) AS sale_month,

            SUM(cs.gross_sales) AS total_gross_sales,

            COUNT(cs.sale_id) AS total_sales

        FROM customer_sales cs

        GROUP BY YEAR(cs.date), MONTH(cs.date)

        ORDER BY sale_year, sale_month;

    """,

    "Q20 — Payment method-wise total collection": """

        SELECT

            payment_method,

            SUM(amount_paid) AS total_collection

        FROM payment_splits

        GROUP BY payment_method

        ORDER BY total_collection DESC;

    """

}

selected_query_name = st.selectbox(

    "Select a predefined SQL query",

    list(sql_queries.keys())

)

selected_sql = sql_queries[selected_query_name]

st.code(

    selected_sql.strip(),

    language="sql"

)

run_sql = st.button(

    "▶️ Run Selected Query"

)

if run_sql:

    try:

        admin_query = selected_sql.strip()

        if st.session_state.role == "Admin":

            branch_id = int(st.session_state.branch_id)

            admin_queries = {

                "Q1 — Retrieve all customer sales": f"SELECT * FROM customer_sales WHERE branch_id = {branch_id} ORDER BY sale_id;",

                "Q4 — Display all Open sales": f"SELECT * FROM customer_sales WHERE branch_id = {branch_id} AND status = 'Open' ORDER BY sale_id;",
                "Q5 — Retrieve Chennai branch sales": f"SELECT cs.* FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id WHERE b.branch_name = 'Chennai' AND cs.branch_id = {branch_id} ORDER BY cs.sale_id;",

                "Q6 — Calculate total gross sales": f"SELECT COALESCE(SUM(gross_sales), 0) AS total_gross_sales FROM customer_sales WHERE branch_id = {branch_id};",

                "Q7 — Calculate total received amount": f"SELECT COALESCE(SUM(received_amount), 0) AS total_received_amount FROM customer_sales WHERE branch_id = {branch_id};",

                "Q8 — Calculate total pending amount": f"SELECT COALESCE(SUM(pending_amount), 0) AS total_pending_amount FROM customer_sales WHERE branch_id = {branch_id};",

                "Q10 — Find average gross sales": f"SELECT AVG(gross_sales) AS average_gross_sales FROM customer_sales WHERE branch_id = {branch_id};",

                "Q11 — Sales details with branch name": f"SELECT cs.sale_id, b.branch_name, cs.date, cs.name, cs.mobile_number, cs.product_name, cs.gross_sales, cs.received_amount, cs.pending_amount, cs.status FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id WHERE cs.branch_id = {branch_id} ORDER BY cs.sale_id;",

                "Q12 — Sales details with branch and customer": f"SELECT b.branch_name, cs.sale_id, cs.name AS customer_name, cs.product_name, cs.gross_sales, cs.received_amount, cs.pending_amount FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id WHERE cs.branch_id = {branch_id} ORDER BY cs.sale_id;",

                "Q13 — Branch-wise total gross sales": f"SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales FROM branches b JOIN customer_sales cs ON b.branch_id = cs.branch_id WHERE cs.branch_id = {branch_id} GROUP BY b.branch_id, b.branch_name;",

                "Q14 — Sales with payment method": f"SELECT cs.sale_id, cs.name AS customer_name, cs.product_name, ps.payment_method, ps.amount_paid, ps.payment_date FROM customer_sales cs JOIN payment_splits ps ON cs.sale_id = ps.sale_id WHERE cs.branch_id = {branch_id} ORDER BY cs.sale_id, ps.payment_id;",

                "Q15 — Detailed sales payment information": f"SELECT cs.sale_id, b.branch_name, cs.name AS customer_name, cs.gross_sales, ps.payment_date, ps.amount_paid, ps.payment_method FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id JOIN payment_splits ps ON cs.sale_id = ps.sale_id WHERE cs.branch_id = {branch_id} ORDER BY cs.sale_id, ps.payment_id;",

                "Q16 — Sales with pending amount greater than 5000": f"SELECT cs.sale_id, b.branch_name, cs.name AS customer_name, cs.gross_sales, cs.received_amount, cs.pending_amount FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id WHERE cs.branch_id = {branch_id} AND cs.pending_amount > 5000 ORDER BY cs.pending_amount DESC;",

                "Q17 — Top 3 highest gross sales": f"SELECT cs.sale_id, b.branch_name, cs.name AS customer_name, cs.product_name, cs.gross_sales FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id WHERE cs.branch_id = {branch_id} ORDER BY cs.gross_sales DESC LIMIT 3;",

                "Q19 — Monthly sales summary": f"SELECT YEAR(cs.date) AS sale_year, MONTH(cs.date) AS sale_month, SUM(cs.gross_sales) AS total_gross_sales, COUNT(cs.sale_id) AS total_sales FROM customer_sales cs WHERE cs.branch_id = {branch_id} GROUP BY YEAR(cs.date), MONTH(cs.date) ORDER BY sale_year, sale_month;"

            }

            if selected_query_name not in admin_queries:

                st.warning("This query is restricted to Super Admin because it can show information across branches.")

            else:

                admin_query = admin_queries[selected_query_name]

                cursor.execute(admin_query)

                query_results = cursor.fetchall()

                if query_results:

                    result_df = pd.DataFrame(query_results)

                    st.success(f"Query executed successfully — {len(result_df)} row(s) returned.")

                    st.dataframe(result_df, use_container_width=True)

                else:

                    st.info("Query executed successfully, but returned no rows.")

        else:

            cursor.execute(admin_query)

            query_results = cursor.fetchall()

            if query_results:

                result_df = pd.DataFrame(query_results)

                st.success(f"Query executed successfully — {len(result_df)} row(s) returned.")

                st.dataframe(result_df, use_container_width=True)

            else:

                st.info("Query executed successfully, but returned no rows.")

    except Error as e:

        st.error(f"SQL execution error: {e}")

# CLOSE CONNECTION

# =========================================================

cursor.close()

conn.close()
