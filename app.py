from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # заміни на свій секретний ключ

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

# ========== Додавання ВЕЛИКИХ округів ==========
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

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO big_districts (district_number, last_name, first_name, middle_name, phone, pickup_points) VALUES (?, ?, ?, ?, ?, ?)',
                  (district_number, last_name, first_name, middle_name, phone, pickup_points))
        conn.commit()
        conn.close()

        return redirect(url_for('big_list'))

    return render_template('add_big.html')

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

# ========== Заглушки для решти ==========
@app.route('/small_list')
def small_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Список малих округів (тимчасово)"

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
