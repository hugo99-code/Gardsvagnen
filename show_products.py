import sqlite3

with sqlite3.connect('database.db') as conn:
    c = conn.cursor()
    c.execute('SELECT id, name, category, weight_kg, description, added_to_vagn FROM products')
    rows = c.fetchall()

print("📦 Produkter i databasen:\n")
for row in rows:
    print(f"ID: {row[0]}, Namn: {row[1]}, Kategori: {row[2]}, Vikt: {row[3]} kg, Beskrivning: {row[4]}, Tillagd i vagn: {row[5]}")
