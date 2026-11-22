import os
import pandas as pd
from database import get_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_path = os.path.join(BASE_DIR, "datasets", "movies.csv")

movies = pd.read_csv(movies_path)

# 🔥 FIX DATE FORMAT
movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')
movies['release_date'] = movies['release_date'].dt.strftime('%Y-%m-%d')

conn = get_db()
cursor = conn.cursor()

count = 0

for _, row in movies.iterrows():
    try:
        cursor.execute("""
            INSERT INTO movies (id, title, overview, release_date, vote_average)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            row['id'],
            row['title'],
            row['overview'],
            row['release_date'],
            row['vote_average']
        ))
        count += 1
    except Exception as e:
        print("Error:", e)

conn.commit()
conn.close()

print("Movies inserted:", count)