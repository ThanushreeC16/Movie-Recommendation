from database import get_db

conn = get_db()
cursor = conn.cursor()

cursor.execute("SHOW TABLES;")
for table in cursor:
    print(table)

conn.close()