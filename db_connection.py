import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="REDACTED",
    database="sales_intelligence_hub"
)

if connection.is_connected():
    print("MySQL connection successful!")

connection.close()