import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_db

conn = get_db()
cursor = conn.cursor(dictionary=True)

cursor.execute("SELECT title FROM movies LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()