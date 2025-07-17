import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# ======= Ініціалізація бази даних =======
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
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

        # Малі округи
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

        # Старші
        c.execute('''
            CREATE TABLE IF NOT EXISTS elders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                big_district TEXT,
                small_district TEXT,
                location TEXT,
                last_name TEXT,
                first_name TEXT,
                middle_name TEXT,
                phone TEXT,
                address TEXT,
                birthdate TEXT,
                subscriber_count INTEGER,
                newspaper_count INTEGER
            )
        ''')

        conn.commit()
        conn.close()

# ======= Користувачі =======
users = {
    'alina01': {'password': '0esz257C', 'role': 'admin'},
    'natalia01': {'password': 'gY7zBv3p', 'role': 'operator'}
}

# ======= Авторизація =======
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

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# ======= ВЕЛИКІ округи =======
@app.route('/big_list')
def big_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM big_districts')
    bigs = c.fetchall()
    conn.close()
    return render_template('big_list.html', bigs=bigs)

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

        conn = sqlite3.connect(DATABASE)
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

@app.route('/edit_big/<int:id>', methods=['GET', 'POST'])
def edit_big(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == 'POST':
        district_number = request.form['district_number']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        phone = request.form['phone']
        pickup_points = ', '.join(request.form.getlist('pickup_points'))

        c.execute('''
            UPDATE big_districts 
            SET district_number=?, last_name=?, first_name=?, middle_name=?, phone=?, pickup_points=? 
            WHERE id=?
        ''', (district_number, last_name, first_name, middle_name, phone, pickup_points, id))
        conn.commit()
        conn.close()
        return redirect(url_for('big_list'))

    c.execute('SELECT * FROM big_districts WHERE id = ?', (id,))
    big = c.fetchone()
    conn.close()

    districts = [str(i) for i in range(1, 7)]
    locations = [f'Л{i}' for i in range(1, 21)]
    selected_locations = big[6].split(', ') if big[6] else []

    return render_template('edit_big.html', big=big, districts=districts, locations=locations, selected_locations=selected_locations)

@app.route('/delete_big/<int:id>', methods=['POST'])
def delete_big(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM big_districts WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('big_list'))

# ======= МАЛІ округи =======
@app.route('/small_list')
def small_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM small_districts')
    smalls = c.fetchall()
    conn.close()

    return render_template('small_list.html', smalls=smalls)

@app.route('/add_small', methods=['GET', 'POST'])
def add_small():
    if 'username' not in session:
        return redirect(url_for('login'))

    local_numbers = [str(i) for i in range(1, 43)]
    locations = [f"Л{i}" for i in range(1, 21)]

    def get_big_district(number):
        n = int(number)
        if 1 <= n <= 7: return "1"
        elif 8 <= n <= 14: return "2"
        elif 15 <= n <= 19: return "3"
        elif 20 <= n <= 28: return "4"
        elif 29 <= n <= 35: return "5"
        elif 36 <= n <= 42: return "6"
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

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO small_districts 
            (big_district, local_number, last_name, first_name, middle_name, address, phone, birth_date, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (big_district, local_number, last_name, first_name, middle_name, address, phone, birth_date, location))
        conn.commit()
        conn.close()

        return redirect(url_for('small_list'))

    return render_template('add_small.html', local_numbers=local_numbers, locations=locations)

@app.route('/edit_small/<int:id>', methods=['GET', 'POST'])
def edit_small(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    locations = [f"Л{i}" for i in range(1, 21)]
    local_numbers = [str(i) for i in range(1, 43)]

    def get_big_district(number):
        n = int(number)
        if 1 <= n <= 7: return "1"
        elif 8 <= n <= 14: return "2"
        elif 15 <= n <= 19: return "3"
        elif 20 <= n <= 28: return "4"
        elif 29 <= n <= 35: return "5"
        elif 36 <= n <= 42: return "6"
        return "Невідомо"

    conn = sqlite3.connect(DATABASE)
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

@app.route('/delete_small/<int:id>', methods=['POST'])
def delete_small(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM small_districts WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('small_list'))

# ======= СТАРШІ =======
@app.route('/elder_list')
def elder_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM elders')
    elders = c.fetchall()
    conn.close()
    return render_template('elder_list.html', elders=elders)

@app.route('/add_elder', methods=['GET', 'POST'])
def add_elder():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        small_district = request.form.get('small_district') or ''
        big_district = request.form.get('big_district') or ''
        location = request.form.get('location') or ''
        last_name = request.form.get('last_name') or ''
        first_name = request.form.get('first_name') or ''
        middle_name = request.form.get('middle_name') or ''
        phone = request.form.get('phone') or ''
        address = request.form.get('address') or ''
        birthdate = request.form.get('birthdate') or ''
        subscriber_count = request.form.get('subscriber_count') or '0'
        newspaper_count = request.form.get('newspaper_count') or '0'

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO elders (
                big_district, small_district, location,
                last_name, first_name, middle_name,
                phone, address, birthdate,
                subscriber_count, newspaper_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            big_district, small_district, location,
            last_name, first_name, middle_name,
            phone, address, birthdate,
            subscriber_count, newspaper_count
        ))
        conn.commit()
        conn.close()

        return redirect(url_for('elder_list'))

    return render_template('add_elder.html')

@app.route('/edit_elder/<int:elder_id>', methods=['GET', 'POST'])
def edit_elder(elder_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        big_district = request.form.get('big_district') or ''
        small_district = request.form.get('small_district') or ''
        location = request.form.get('location') or ''
        last_name = request.form.get('last_name') or ''
        first_name = request.form.get('first_name') or ''
        middle_name = request.form.get('middle_name') or ''
        phone = request.form.get('phone') or ''
        address = request.form.get('address') or ''
        birthdate = request.form.get('birthdate') or ''
        subscriber_count = request.form.get('subscriber_count') or '0'
        newspaper_count = request.form.get('newspaper_count') or '0'

        c.execute('''
            UPDATE elders SET
                big_district = ?, small_district = ?, location = ?,
                last_name = ?, first_name = ?, middle_name = ?,
                phone = ?, address = ?, birthdate = ?,
                subscriber_count = ?, newspaper_count = ?
            WHERE id = ?
        ''', (
            big_district, small_district, location,
            last_name, first_name, middle_name,
            phone, address, birthdate,
            subscriber_count, newspaper_count,
            elder_id
        ))

        conn.commit()
        conn.close()
        flash("Анкету оновлено успішно!", "success")
        return redirect(url_for('elder_list'))

    c.execute('SELECT * FROM elders WHERE id = ?', (elder_id,))
    elder = c.fetchone()
    conn.close()

    if elder is None:
        flash("Анкета не знайдена.", "error")
        return redirect(url_for('elder_list'))

    return render_template('edit_elder.html', elder=elder)

@app.route('/delete_elder/<int:id>', methods=['POST'])
def delete_elder(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM elders WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('elder_list'))

@app.route('/subscriber_list')
def subscriber_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Список підписників (тимчасово)"

# ======= Запуск =======
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
