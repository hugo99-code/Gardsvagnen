import sqlite3

print("🛡️ Lägg till en adminanvändare\n")

username = input("Användarnamn: ")
password = input("Lösenord: ")

with sqlite3.connect('database.db') as conn:
    c = conn.cursor()
    try:
        c.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, password))
        print(f"✅ Admin '{username}' har skapats.")
    except sqlite3.IntegrityError:
        print(f"⚠️ Admin-användarnamnet '{username}' finns redan.")
