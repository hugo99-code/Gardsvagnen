import sqlite3

print("🛠️ Hantera förare (ändra eller ta bort)")

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("SELECT username FROM drivers")
    drivers = c.fetchall()

    if not drivers:
        print("❌ Det finns inga förare registrerade.")
        exit()

    print("\n📋 Förares användarnamn:")
    for d in drivers:
        print(f"- {d[0]}")

username = input("\nAnge användarnamn att hantera: ").strip()

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM drivers WHERE username = ?", (username,))
    result = c.fetchone()

    if not result:
        print(f"❌ Ingen förare med användarnamnet '{username}' hittades.")
    else:
        driver_id, current_username, current_password = result
        print(f"\n✅ Förare hittad: {current_username}")

        print("\n1. Ändra användarnamn/lösenord\n2. Radera förare\n3. Avbryt")
        choice = input("Val (1/2/3): ").strip()

        if choice == "1":
            new_username = input("Nytt användarnamn (Enter för att behålla): ").strip()
            new_password = input("Nytt lösenord (Enter för att behålla): ").strip()

            if new_username == "":
                new_username = current_username
            if new_password == "":
                new_password = current_password

            c.execute("UPDATE drivers SET username = ?, password = ? WHERE id = ?", (new_username, new_password, driver_id))
            conn.commit()
            print("✅ Förare uppdaterad.")

        elif choice == "2":
            confirm = input("⚠️ Bekräfta radering (ja/nej): ").strip().lower()
            if confirm == "ja":
                c.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
                conn.commit()
                print("🗑️ Förare raderad.")
            else:
                print("❌ Avbrutet.")
        else:
            print("🚫 Inget ändrades.")
