from flask import g
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecret'

# Skapa databasen om den inte finns
def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()

        # Bönder
        c.execute('''
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                farm_name TEXT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')

        # Admins
        c.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')

        # Produkter
        c.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER,
                name TEXT,
                category TEXT,
                weight_kg REAL,
                description TEXT,
                added_to_vagn INTEGER DEFAULT 0
            )
        ''')

        # Förare
        c.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')

@app.context_processor
def inject_farmer_image():
    if 'user_id' in session:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT image_path FROM farmers WHERE id = ?", (session['user_id'],))
            result = c.fetchone()
            return {'farmer_image': result[0] if result and result[0] else None}
    return {'farmer_image': None}

@app.route("/alla-tabeller")
def alla_tabeller():
    con = sqlite3.connect("databas.db")
    cur = con.cursor()

    tabeller = ["product", "farmer", "user", "driver", "admin", "wagon"]  # lägg till dina
    data = {}

    for tabell in tabeller:
        cur.execute(f"SELECT * FROM {tabell}")
        rows = cur.fetchall()

        cur.execute(f"PRAGMA table_info({tabell})")
        columns = [col[1] for col in cur.fetchall()]

        data[tabell] = {
            "columns": columns,
            "rows": rows
        }

    con.close()
    return render_template("alla_tabeller.html", data=data)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        role = request.form['role']

        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()

            if role == 'farmer':
                c.execute('SELECT id FROM farmers WHERE username=? AND password=?', (user, pwd))
                result = c.fetchone()
                if result:
                    session['user_id'] = result[0]
                    return redirect('/farmer/menu')

            elif role == 'admin':
                c.execute('SELECT id FROM admins WHERE username=? AND password=?', (user, pwd))
                result = c.fetchone()
                if result:
                    session['admin_id'] = result[0]
                    return redirect('/admin/menu')

            elif role == 'driver':
                c.execute('SELECT id FROM drivers WHERE username=? AND password=?', (user, pwd))
                result = c.fetchone()
                if result:
                    session['driver_id'] = result[0]
                    return redirect('/driver/menu')

        error = "Fel användarnamn, lösenord eller roll."

    return render_template('login.html', error=error)

@app.route('/register_farmer', methods=['GET', 'POST'])
def register_farmer():
    if request.method == 'POST':
        name = request.form['name']
        farm_name = request.form['farm_name']
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO farmers (name, farm_name, username, password) VALUES (?, ?, ?, ?)',
                      (name, farm_name, username, password))
        return redirect('/')
    return render_template('register_farmer.html')

@app.route('/register', methods=['GET', 'POST'])
def register_product():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        weight = request.form['weight']
        desc = request.form['description']
        unit = request.form['unit']  # 👈 nytt

        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO products (farmer_id, name, category, weight_kg, description, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], name, category, weight, desc, unit))
        return redirect('/register')
    return render_template('register_product.html')

@app.route('/admin/select_farm', methods=['GET', 'POST'])
def select_farm():
    if 'admin_id' not in session:
        return redirect('/')
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT DISTINCT id, farm_name FROM farmers ORDER BY farm_name')
        farms = c.fetchall()
    if request.method == 'POST':
        selected_farm_id = request.form['farm_id']
        return redirect(f'/admin/farm/{selected_farm_id}')
    return render_template('select_farm.html', farms=farms)

@app.route('/admin/farm/<int:farm_id>', methods=['GET', 'POST'])
def view_farm_products(farm_id):
    if 'admin_id' not in session:
        return redirect('/')

    categories = [
        "Kött & Fågel",
        "Frukt & Grönt",
        "Ägg & Mejeri",
        "Bröd & Bullar",
        "Övrigt"
    ]

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        if request.method == 'POST':
            product_id = request.form['product_id']
            action = request.form['action']
            if action == 'add':
                c.execute('UPDATE products SET added_to_vagn = 1 WHERE id = ?', (product_id,))
            elif action == 'remove':
                c.execute('UPDATE products SET added_to_vagn = 0 WHERE id = ?', (product_id,))
        
        c.execute('SELECT farm_name FROM farmers WHERE id = ?', (farm_id,))
        farm_name = c.fetchone()[0]

        # Hämta alla produkter för gården
        c.execute('''
            SELECT id, name, category, weight_kg, description, added_to_vagn
            FROM products
            WHERE farmer_id = ?
        ''', (farm_id,))
        all_products = c.fetchall()

    # Sortera produkter i en dict per kategori
    products_by_category = {cat: [] for cat in categories}
    for product in all_products:
        cat = product[2]
        if cat in products_by_category:
            products_by_category[cat].append(product)
        else:
            products_by_category["Övrigt"].append(product)

    return render_template('farm_products.html', farm_name=farm_name, products_by_category=products_by_category)

@app.route('/admin/vagnen', methods=['GET', 'POST'])
def view_vagn_products():
    if 'admin_id' not in session:
        return redirect('/')

    categories = ["Kött & Fågel", "Frukt & Grönt", "Ägg & Mejeri", "Bröd & Bullar", "Övrigt"]

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT products.id, products.name, products.category, products.weight_kg,
                   products.unit, products.description, farmers.farm_name
            FROM products
            JOIN farmers ON products.farmer_id = farmers.id
            WHERE products.added_to_vagn = 1
        ''')
        vagn_products = c.fetchall()

    products_by_category = {cat: [] for cat in categories}
    for p in vagn_products:
        category = p[2]
        if category in products_by_category:
            products_by_category[category].append(p)
        else:
            products_by_category["Övrigt"].append(p)

    return render_template('vagnen.html', products_by_category=products_by_category)

@app.route('/driver_login', methods=['GET', 'POST'])
def driver_login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM drivers WHERE username=? AND password=?', (user, pwd))
            result = c.fetchone()
            if result:
                session['driver_id'] = result[0]
                return redirect('/driver/menu')
    return render_template('driver_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/driver/pickup', methods=['GET', 'POST'])
def driver_pickup():
    if 'driver_id' not in session:
        return redirect('/')

    driver_id = session['driver_id']

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()

        # Checka av produkter (om POST)
        if request.method == 'POST':
            product_id = request.form['product_id']
            # Lägg till i picked_up_products om inte redan finns
            c.execute('''
                INSERT OR IGNORE INTO picked_up_products (product_id, driver_id)
                VALUES (?, ?)
            ''', (product_id, driver_id))
            conn.commit()

        # Hämta alla produkter i vagnen som INTE är upphämtade av denna förare
        c.execute('''
            SELECT products.id, products.name, products.category, products.weight_kg,
                   farmers.farm_name
            FROM products
            JOIN farmers ON products.farmer_id = farmers.id
            WHERE products.added_to_vagn = 1 AND products.id NOT IN (
                SELECT product_id FROM picked_up_products WHERE driver_id = ?
            )
        ''', (driver_id,))
        result = c.fetchall()

    # Gruppera efter gård
    products_by_farm = {}
    for p in result:
        farm = p[4]
        if farm not in products_by_farm:
            products_by_farm[farm] = []
        products_by_farm[farm].append(p)

    return render_template('driver_pickup.html', products_by_farm=products_by_farm)

@app.route('/driver/vagn', methods=['GET', 'POST'])
def driver_vagn():
    if 'driver_id' not in session:
        return redirect('/')

    driver_id = session['driver_id']

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()

        # Hantera "slutsåld"-radering
        if request.method == 'POST':
            product_id = request.form['product_id']
            # Ta bort från picked_up_products
            c.execute('DELETE FROM picked_up_products WHERE product_id = ? AND driver_id = ?', (product_id, driver_id))
            # Ta bort från products
            c.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()

        # Visa alla produkter som denna förare har hämtat upp
        c.execute('''
            SELECT products.id, products.name, products.category, products.weight_kg,
            farmers.farm_name, products.unit
            FROM picked_up_products
            JOIN products ON picked_up_products.product_id = products.id
            JOIN farmers ON products.farmer_id = farmers.id
            WHERE picked_up_products.driver_id = ?
        ''', (driver_id,))
        result = c.fetchall()

    # Gruppera per kategori och gård
    structured = {}
    for product_id, name, category, weight, farm, unit in result:
        if category not in structured:
            structured[category] = {}
        if farm not in structured[category]:
            structured[category][farm] = []
        structured[category][farm].append((product_id, name, weight, unit))

    return render_template('driver_vagn.html', structured=structured)

@app.route('/driver/menu')
def driver_menu():
    if 'driver_id' not in session:
        return redirect('/')
    return render_template('driver_menu.html')

@app.route('/admin/menu')
def admin_menu():
    if 'admin_id' not in session:
        return redirect('/')
    return render_template('admin_menu.html')

@app.route('/farmer/menu')
def farmer_menu():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('farmer_menu.html')

@app.route('/logout_driver')
def logout_driver():
    session.pop('driver_id', None)
    return redirect('/')

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/farmer/profile', methods=['GET', 'POST'])
def farmer_profile():
    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()

        if request.method == 'POST':
            name = request.form['name']
            farm_name = request.form['farm_name']
            username = request.form['username']
            password = request.form['password']

            # Hantera ny bild
            remove_image = 'remove_image' in request.form
            image = request.files.get('image')
            image_path = None

            if remove_image:
                c.execute("SELECT image_path FROM farmers WHERE id = ?", (user_id,))
                current_image = c.fetchone()[0]
                if current_image and os.path.exists(current_image):
                    os.remove(current_image)
                image_path = None
            elif image and image.filename:
                filename = secure_filename(f"{user_id}_{image.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                image_path = filepath

            # Uppdatera databasen
            if image_path is not None or remove_image:
                c.execute('''
                    UPDATE farmers SET name=?, farm_name=?, username=?, password=?, image_path=?
                    WHERE id=?
                ''', (name, farm_name, username, password, image_path, user_id))
            else:
                c.execute('''
                    UPDATE farmers SET name=?, farm_name=?, username=?, password=?
                    WHERE id=?
                ''', (name, farm_name, username, password, user_id))

            conn.commit()

        c.execute('SELECT name, farm_name, username, password, image_path FROM farmers WHERE id=?', (user_id,))
        farmer = c.fetchone()

    return render_template('farmer_profile.html', farmer=farmer)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
