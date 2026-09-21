from db import get_connection


connection = get_connection()
print("connected to PostgreSQL!")
connection.close()
