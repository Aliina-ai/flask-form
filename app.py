from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 🔐 Заміни на свій власний ключ

DB_NAME = 'data.db'

# Ініціалізація бази даних
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # Таблиця користувачів
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        # Таблиця підписників
        c.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                newspaper TEXT,
                term TEXT,
                created_by TEXT
            )
        ''')

        # Таблиця великих округів
        c.execute('''
            CREATE TABLE IF NOT EXISTS big_districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district_number INTEGER NOT NULL,
                last_name TEXT,
                first_name TEXT,
                middle_name TEXT,
                phone TEXT,
                pickup_points TEXT
            )
        ''')

        # Створення користувачів (один раз)
        c.execute("SELECT * FROM users WHERE username = 'alina01'")
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('alina01', '0esz257C', 'admin'))
        c.execute("SELECT * FROM users WHERE username = 'natalia01'")
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('natalia01', 'mF39vAq2', 'operator'))

        conn.commit()

# Головна
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

# Вхід
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                session['username'] = username
                session['role'] = user[3]
                return redirect(url_for('add_subscriber'))
            else:
                error = "Невірний логін або пароль"
    return render_template('login.html', error=error)

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# Вихід
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Додати підписника
@app.route('/add', methods=['GET', 'POST'])
def add_subscriber():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        newspaper = request.form['newspaper']
        term = request.form['term']
        created_by = session['username']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO subscribers (name, address, phone, newspaper, term, created_by)
                VALUES (1, 2, 3, 4, 5, 6)
            ''', (name, address, phone, newspaper, term, created_by))
            conn.commit()
        return "Підписника додано!"
    return render_template('add.html')

# Перегляд підписників
@app.route('/subscribers')
def show_subscribers():
    if 'username' not in session or session['role'] not in ['admin', 'operator']:
        return "Доступ заборонено"
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM subscribers")
        subscribers = c.fetchall()
    return render_template('subscribers.html', subscribers=subscribers)

# Додати великий округ
@app.route('/add_big', methods=['GET', 'POST'])
def add_big():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        district_number = request.form['district_number']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        phone = request.form['phone']
        pickup_points = request.form['pickup_points']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO big_districts (
                    district_number, last_name, first_name,
                    middle_name, phone, pickup_points
                ) VALUES (1, 2, 3, 4, 5, 6)
            ''', (district_number, last_name, first_name, middle_name, phone, pickup_points))
            conn.commit()
        return "Округ додано успішно!"
    return render_template('add_big.html')

# Перегляд великих округів
@app.route('/big_list')
def big_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM big_districts ORDER BY district_number")
        districts = c.fetchall()
    return render_template('big_list.html', districts=districts)

# Запуск локально або на сервері
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
