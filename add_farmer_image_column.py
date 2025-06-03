import sqlite3

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("ALTER TABLE farmers ADD COLUMN image_path TEXT")
    conn.commit()

print("✅ Kolumn 'image_path' har lagts till i tabellen 'farmers'.")
