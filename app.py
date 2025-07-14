from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 🔐 заміни на свій секретний ключ

DB_NAME = 'data.db'

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
        # Створення користувачів (якщо їх ще немає)
        c.execute("SELECT * FROM users WHERE username = 'alina01'")
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('alina01', '0esz257C', 'admin'))
        c.execute("SELECT * FROM users WHERE username = 'natalia01'")
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('natalia01', 'mF39vAq2', 'operator'))
        conn.commit()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('add_subscriber'))

@app.route('/login', methods=['GET', 'POST'])
def login():
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
                return "Невірний логін або пароль"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, address, phone, newspaper, term, created_by))
            conn.commit()
        return "Підписника додано!"
    return render_template('add.html')

@app.route('/subscribers')
def show_subscribers():
    if 'username' not in session or session['role'] != 'admin':
        return "Доступ заборонено"
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM subscribers")
        subscribers = c.fetchall()
    return render_template('subscribers.html', subscribers=subscribers)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
