import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # заміни на свій секретний ключ

# ========== Ініціалізація бази ==========
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Великі округи
    c.execute('''
        CREATE TABLE IF NOT EXISTS big_districts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district_number TEXT NOT NULL,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            phone TEXT,
            pickup_points TEXT
        )
    ''')

    # Малі округи (Великий округ перший!)
    c.execute('''
        CREATE TABLE IF NOT EXISTS small_districts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            big_district TEXT,
            local_number TEXT NOT NULL,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            address TEXT,
            phone TEXT,
            birth_date TEXT,
            location TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ========== Користувачі ==========
users = {
    'alina01': {'password': '0esz257C', 'role': 'admin'},
    'natalia01': {'password': 'gY7zBv3p', 'role': 'operator'}  # Згенерований пароль
}

# ========== Авторизація ==========
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = users.get(login)
        if user and user['password'] == password:
            session['username'] = login
            session['role'] = user['role']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Невірний логін або пароль")
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

# ========== Головна сторінка ==========
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# ========== Список ВЕЛИКИХ округів ==========
@app.route('/big_list')
def big_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM big_districts')
    bigs = c.fetchall()
    conn.close()
    return render_template('big_list.html', bigs=bigs)

# ========== Додавання анкети великого округу ==========
@app.route('/add_big', methods=['GET', 'POST'])
def add_big():
    if 'username' not in session:
        return redirect(url_for('login'))

    districts = [str(i) for i in range(1, 7)]
    locations = [f'Л{i}' for i in range(1, 21)]

    if request.method == 'POST':
        district_number = request.form['district_number']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        phone = request.form['phone']
        pickup_points = ', '.join(request.form.getlist('pickup_points'))

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO big_districts 
            (district_number, last_name, first_name, middle_name, phone, pickup_points)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (district_number, last_name, first_name, middle_name, phone, pickup_points))
        conn.commit()
        conn.close()
        return redirect(url_for('big_list'))

    return render_template('add_big.html', districts=districts, locations=locations)

# 🗑️ Видалення відповідального
@app.route('/delete_big/<int:id>', methods=['POST'])
def delete_big(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM big_districts WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('big_list'))

# ✏️ Редагування відповідального
@app.route('/edit_big/<int:id>', methods=['GET', 'POST'])
def edit_big(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        district_number = request.form['district_number']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        phone = request.form['phone']
        pickup_points = ', '.join(request.form.getlist('pickup_points'))

        c.execute('''UPDATE big_districts 
                     SET district_number=?, last_name=?, first_name=?, middle_name=?, phone=?, pickup_points=? 
                     WHERE id=?''',
                  (district_number, last_name, first_name, middle_name, phone, pickup_points, id))
        conn.commit()
        conn.close()
        return redirect(url_for('big_list'))

    c.execute("SELECT * FROM big_districts WHERE id = ?", (id,))
    big = c.fetchone()
    conn.close()

    districts = [str(i) for i in range(1, 7)]
    locations = [f'Л{i}' for i in range(1, 21)]
    selected_locations = big[6].split(', ') if big[6] else []

    return render_template('edit_big.html', big=big, districts=districts, locations=locations, selected_locations=selected_locations)

# ========== Список МАЛИХ округів ==========
@app.route('/small_list')
def small_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM small_districts')
    smalls = c.fetchall()
    conn.close()

    return render_template('small_list.html', smalls=smalls)

# ========== Додавання анкети малого округу ==========
@app.route('/add_small', methods=['GET', 'POST'])
def add_small():
    if 'username' not in session:
        return redirect(url_for('login'))

    local_numbers = [str(i) for i in range(1, 43)]
    locations = [f"Л{i}" for i in range(1, 21)]

    def get_big_district(number):
        n = int(number)
        if 1 <= n <= 7:
            return "1"
        elif 8 <= n <= 14:
            return "2"
        elif 15 <= n <= 19:
            return "3"
        elif 20 <= n <= 28:
            return "4"
        elif 29 <= n <= 35:
            return "5"
        elif 36 <= n <= 42:
            return "6"
        return "Невідомо"

    if request.method == 'POST':
        local_number = request.form['local_number']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        address = request.form['address']
        phone = request.form['phone']
        birth_date = request.form['birth_date']
        location = request.form['location']
        big_district = get_big_district(local_number)

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO small_districts 
            (big_district, local_number, last_name, first_name, middle_name, address, phone, birth_date, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (big_district, local_number, last_name, first_name, middle_name, address, phone, birth_date, location))
        conn.commit()
        conn.close()

        return redirect(url_for('small_list'))

    return render_template(
        'add_small.html',
        local_numbers=local_numbers,
        locations=locations
    )

# ========== Редагування анкети малого округу ==========
@app.route('/edit_small/<int:id>', methods=['GET', 'POST'])
def edit_small(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    locations = [f"Л{i}" for i in range(1, 21)]
    local_numbers = [str(i) for i in range(1, 43)]

    def get_big_district(number):
        n = int(number)
        if 1 <= n <= 7:
            return "1"
        elif 8 <= n <= 14:
            return "2"
        elif 15 <= n <= 19:
            return "3"
        elif 20 <= n <= 28:
            return "4"
        elif 29 <= n <= 35:
            return "5"
        elif 36 <= n <= 42:
            return "6"
        return "Невідомо"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        local_number = request.form['local_number']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        address = request.form['address']
        phone = request.form['phone']
        birth_date = request.form['birth_date']
        location = request.form['location']
        big_district = get_big_district(local_number)

        c.execute('''
            UPDATE small_districts SET 
                big_district = ?, local_number = ?, last_name = ?, 
                first_name = ?, middle_name = ?, address = ?, 
                phone = ?, birth_date = ?, location = ? 
            WHERE id = ?
        ''', (big_district, local_number, last_name, first_name, middle_name,
              address, phone, birth_date, location, id))

        conn.commit()
        conn.close()
        return redirect(url_for('small_list'))

    c.execute('SELECT * FROM small_districts WHERE id = ?', (id,))
    small = c.fetchone()
    conn.close()

    return render_template('edit_small.html', small=small, locations=locations, local_numbers=local_numbers)

# ========== Видалення  анкети малого округа ==========

@app.route('/delete_small/<int:id>', methods=['POST'])
def delete_small(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM small_districts WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('small_list'))

# ========== Заглушки для решти ==========
@app.route('/elder_list')
def elder_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Список старших (тимчасово)"

@app.route('/subscriber_list')
def subscriber_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Список підписників (тимчасово)"

# ========== Запуск ==========
if __name__ == '__main__':
    init_db()  # ⬅️ Перший запуск створює базу
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
