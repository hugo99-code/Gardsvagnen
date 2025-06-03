import sqlite3

print("🛠️ Hantera bönder (ändra eller ta bort)")

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("SELECT username FROM farmers")
    farmers = c.fetchall()

    if not farmers:
        print("❌ Det finns inga bönder registrerade.")
        exit()

    print("\n📋 Böndernas användarnamn:")
    for f in farmers:
        print(f"- {f[0]}")

username = input("\nAnge användarnamn att hantera: ").strip()

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("SELECT id, name, farm_name, username, password FROM farmers WHERE username = ?", (username,))
    result = c.fetchone()

    if not result:
        print(f"❌ Ingen bonde med användarnamnet '{username}' hittades.")
    else:
        farmer_id, name, farm_name, current_username, current_password = result
        print(f"\n✅ Bonde hittad: {current_username}")

        print("\n1. Ändra info\n2. Radera bonde\n3. Avbryt")
        choice = input("Val (1/2/3): ").strip()

        if choice == "1":
            new_name = input("Nytt namn (Enter för att behålla): ").strip()
            new_farm = input("Nytt gårdsnamn (Enter för att behålla): ").strip()
            new_username = input("Nytt användarnamn (Enter för att behålla): ").strip()
            new_password = input("Nytt lösenord (Enter för att behålla): ").strip()

            if new_name == "":
                new_name = name
            if new_farm == "":
                new_farm = farm_name
            if new_username == "":
                new_username = current_username
            if new_password == "":
                new_password = current_password

            c.execute('''
                UPDATE farmers
                SET name = ?, farm_name = ?, username = ?, password = ?
                WHERE id = ?
            ''', (new_name, new_farm, new_username, new_password, farmer_id))
            conn.commit()
            print("✅ Bonde uppdaterad.")
        elif choice == "2":
            confirm = input("⚠️ Bekräfta radering (ja/nej): ").strip().lower()
            if confirm == "ja":
                c.execute("DELETE FROM farmers WHERE id = ?", (farmer_id,))
                conn.commit()
                print("🗑️ Bonde raderad.")
            else:
                print("❌ Avbrutet.")
        else:
            print("🚫 Inget ändrades.")
