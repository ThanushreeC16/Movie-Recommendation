import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('OMDB_API_KEY')

def fetch(title, year):
    try:
        r = requests.get('http://www.omdbapi.com/', params={'t': title, 'y': year, 'apikey': key}, timeout=5)
        d = r.json()
        if d.get('Response') == 'True':
            return d.get('Poster', ''), d.get('Plot', '')
        # retry without year
        r2 = requests.get('http://www.omdbapi.com/', params={'t': title, 'apikey': key}, timeout=5)
        d2 = r2.json()
        if d2.get('Response') == 'True':
            return d2.get('Poster', ''), d2.get('Plot', '')
    except Exception as e:
        print(f"  Error fetching {title}: {e}")
    return '', ''

df = pd.read_csv('datasets/movies_updated.csv', dtype=str)
mask = df['poster_url'].isna() | (df['poster_url'].str.strip() == '')
missing = df[mask].index.tolist()
print(f"Fetching posters for {len(missing)} movies...")

filled = 0
for i, idx in enumerate(missing):
    name = df.at[idx, 'movie_name']
    year = df.at[idx, 'year']
    poster, plot = fetch(name, year)
    if poster and poster != 'N/A':
        df.at[idx, 'poster_url'] = poster
        filled += 1
    if plot and plot != 'N/A':
        df.at[idx, 'description'] = plot
    if (i + 1) % 50 == 0:
        df.to_csv('datasets/movies_updated.csv', index=False)
        print(f"  Progress: {i+1}/{len(missing)}, filled so far: {filled}")
    time.sleep(0.1)  # avoid rate limiting

df.to_csv('datasets/movies_updated.csv', index=False)
print(f"Done. Filled posters for {filled}/{len(missing)} movies.")
