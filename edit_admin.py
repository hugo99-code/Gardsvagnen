import sqlite3

print("🛠️ Hantera admins (ändra eller ta bort)")

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("SELECT username FROM admins")
    admins = c.fetchall()

    if not admins:
        print("❌ Det finns inga admins registrerade.")
        exit()

    print("\n📋 Admin-användare:")
    for a in admins:
        print(f"- {a[0]}")

username = input("\nAnge användarnamn att hantera: ").strip()

with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM admins WHERE username = ?", (username,))
    result = c.fetchone()

    if not result:
        print(f"❌ Ingen admin med användarnamnet '{username}' hittades.")
    else:
        admin_id, current_username, current_password = result
        print(f"\n✅ Admin hittad: {current_username}")

        print("\n1. Ändra användarnamn/lösenord\n2. Radera admin\n3. Avbryt")
        choice = input("Val (1/2/3): ").strip()

        if choice == "1":
            new_username = input("Nytt användarnamn (Enter för att behålla): ").strip()
            new_password = input("Nytt lösenord (Enter för att behålla): ").strip()

            if new_username == "":
                new_username = current_username
            if new_password == "":
                new_password = current_password

            c.execute("UPDATE admins SET username = ?, password = ? WHERE id = ?", (new_username, new_password, admin_id))
            conn.commit()
            print("✅ Admin uppdaterad.")

        elif choice == "2":
            confirm = input("⚠️ Bekräfta radering (ja/nej): ").strip().lower()
            if confirm == "ja":
                c.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
                conn.commit()
                print("🗑️ Admin raderad.")
            else:
                print("❌ Avbrutet.")
        else:
            print("🚫 Inget ändrades.")
