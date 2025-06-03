import sqlite3

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("ALTER TABLE products ADD COLUMN unit TEXT DEFAULT 'kg'")
    conn.commit()

print("✅ Kolumn 'unit' tillagd i products.")
