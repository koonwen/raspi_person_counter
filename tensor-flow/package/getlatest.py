import sqlite3

conn = sqlite3.connect('data.db')
cur = conn.cursor()
print(cur.execute("SELECT * FROM Data ORDER BY Timestamp DESC LIMIT 10").fetchall())
conn.close()