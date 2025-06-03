import sqlite3

with sqlite3.connect('database.db') as conn:
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS picked_up_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            driver_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        )
    ''')
    conn.commit()

print("✅ Tabell 'picked_up_products' skapad eller fanns redan.")
