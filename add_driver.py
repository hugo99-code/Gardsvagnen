import sqlite3

print("🛠️ Hantera förare (ändra eller ta bort)")

username = input("Ange förarens användarnamn: ").strip()

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM drivers WHERE username = ?", (username,))
    result = c.fetchone()

    if not result:
        print(f"❌ Ingen förare med användarnamnet '{username}' hittades.")
    else:
        driver_id, current_username, current_password = result
        print(f"\n✅ Förare hittad:")
        print(f"- Användarnamn: {current_username}")
        print(f"- Lösenord: {'*' * len(current_password)}")

        print("\nVad vill du göra?")
        print("1. Ändra användarnamn/lösenord")
        print("2. Radera föraren")
        print("3. Avbryt")

        choice = input("Val (1/2/3): ").strip()

        if choice == "1":
            new_username = input("Nytt användarnamn (Enter för att behålla): ").strip()
            new_password = input("Nytt lösenord (Enter för att behålla): ").strip()

            if new_username == "":
                new_username = current_username
            if new_password == "":
                new_password = current_password

            c.execute('''
                UPDATE drivers
                SET username = ?, password = ?
                WHERE id = ?
            ''', (new_username, new_password, driver_id))
            conn.commit()
            print(f"✅ Förare uppdaterad:\n- Nytt användarnamn: {new_username}")

        elif choice == "2":
            confirm = input(f"⚠️ Är du säker på att du vill radera '{username}'? (ja/nej): ").strip().lower()
            if confirm == "ja":
                c.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
                conn.commit()
                print(f"🗑️ Förare '{username}' har raderats.")
            else:
                print("❌ Avbrutet. Föraren är kvar.")
        else:
            print("🚫 Inget ändrades.")
