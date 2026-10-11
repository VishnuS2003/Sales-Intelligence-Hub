
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "sales_intelligence_hub")
    )

if __name__ == "__main__":
    connection = get_connection()
    if connection.is_connected():
        print("MySQL connection successful!")
    connection.close()
