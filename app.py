from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

DB_NAME = 'data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS big_districts (
            id SERIAL PRIMARY KEY,
            district_number TEXT NOT NULL,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            phone TEXT,
            pickup_points TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS small_districts (
            id SERIAL PRIMARY KEY,
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

    cur.execute('''
        CREATE TABLE IF NOT EXISTS elders (
            id SERIAL PRIMARY KEY,
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
    cur.close()
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
        login_user = request.form['login']
        password = request.form['password']
        user = users.get(login_user)
        if user and user['password'] == password:
            session['username'] = login_user
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
    return "Список старших (тимчасово)"

# ======= МАЛІ округи =======
@app.route('/small_list')
def small_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Список старших (тимчасово)"

# ======= СТАРШІ =======
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
