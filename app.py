import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'mysecretkey')

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не заданий у змінних середовища!")


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except psycopg2.Error as e:
        print("⚠️ Помилка підключення до бази даних:", e)
        raise


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

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

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM big_districts ORDER BY id')
    bigs = cur.fetchall()
    cur.close()
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

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO big_districts 
            (district_number, last_name, first_name, middle_name, phone, pickup_points)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (district_number, last_name, first_name, middle_name, phone, pickup_points))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('big_list'))

    return render_template('add_big.html', districts=districts, locations=locations)


@app.route('/edit_big/<int:id>', methods=['GET', 'POST'])
def edit_big(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        district_number = request.form['district_number']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        phone = request.form['phone']
        pickup_points = ', '.join(request.form.getlist('pickup_points'))

        cur.execute('''
            UPDATE big_districts 
            SET district_number=%s, last_name=%s, first_name=%s, middle_name=%s, phone=%s, pickup_points=%s 
            WHERE id=%s
        ''', (district_number, last_name, first_name, middle_name, phone, pickup_points, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('big_list'))

    cur.execute('SELECT * FROM big_districts WHERE id = %s', (id,))
    big = cur.fetchone()
    cur.close()
    conn.close()

    districts = [str(i) for i in range(1, 7)]
    locations = [f'Л{i}' for i in range(1, 21)]
    selected_locations = big[6].split(', ') if big and big[6] else []

    return render_template('edit_big.html', big=big, districts=districts, locations=locations, selected_locations=selected_locations)


@app.route('/delete_big/<int:id>', methods=['POST'])
def delete_big(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM big_districts WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('big_list'))


# ======= МАЛІ округи =======
@app.route('/small_list')
def small_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM small_districts ORDER BY id')
    smalls = cur.fetchall()
    cur.close()
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

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO small_districts 
            (big_district, local_number, last_name, first_name, middle_name, address, phone, birth_date, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (big_district, local_number, last_name, first_name, middle_name, address, phone, birth_date, location))
        conn.commit()
        cur.close()
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

    conn = get_db_connection()
    cur = conn.cursor()

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

        cur.execute('''
            UPDATE small_districts SET 
                big_district = %s, local_number = %s, last_name = %s, 
                first_name = %s, middle_name = %s, address = %s, 
                phone = %s, birth_date = %s, location = %s 
            WHERE id = %s
        ''', (big_district, local_number, last_name, first_name, middle_name,
              address, phone, birth_date, location, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('small_list'))

    cur.execute('SELECT * FROM small_districts WHERE id = %s', (id,))
    small = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit_small.html', small=small, locations=locations, local_numbers=local_numbers)


@app.route('/delete_small/<int:id>', methods=['POST'])
def delete_small(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM small_districts WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('small_list'))


# ======= СТАРШІ =======
@app.route('/elder_list')
def elder_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM elders ORDER BY id')
    elders = cur.fetchall()
    cur.close()
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
        subscriber_count = request.form.get('subscriber_count') or 0
        newspaper_count = request.form.get('newspaper_count') or 0

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO elders (
                big_district, small_district, location,
                last_name, first_name, middle_name,
                phone, address, birthdate,
                subscriber_count, newspaper_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            big_district, small_district, location,
            last_name, first_name, middle_name,
            phone, address, birthdate,
            subscriber_count, newspaper_count
        ))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('elder_list'))

    return render_template('add_elder.html')

@app.route('/edit_elder/<int:elder_id>', methods=['GET', 'POST'])
def edit_elder(elder_id):
    elder = Elder.query.get_or_404(elder_id)

    if request.method == 'POST':
        elder.small_district = int(request.form['small_district'])
        elder.location = request.form.get('location') or None
        elder.last_name = request.form.get('last_name') or None
        elder.first_name = request.form.get('first_name') or None
        elder.middle_name = request.form.get('middle_name') or None
        elder.phone = request.form.get('phone') or None
        elder.address = request.form.get('address') or None
        elder.birth_date = request.form.get('birth_date') or None
        elder.subscribers = request.form.get('subscribers') or None
        elder.newspapers = request.form.get('newspapers') or None

        # Визначення великого округу
        sd = elder.small_district
        if 1 <= sd <= 7:
            elder.big_district = 1
        elif 8 <= sd <= 14:
            elder.big_district = 2
        elif 15 <= sd <= 19:
            elder.big_district = 3
        elif 20 <= sd <= 28:
            elder.big_district = 4
        elif 29 <= sd <= 35:
            elder.big_district = 5
        elif 36 <= sd <= 42:
            elder.big_district = 6
        else:
            elder.big_district = None

        db.session.commit()
        return redirect(url_for('elder_list'))

    return render_template('edit_elder.html', elder=elder)


@app.route('/delete_elder/<int:id>', methods=['POST'])
def delete_elder(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM elders WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('elder_list'))


@app.route('/subscriber_list')
def subscriber_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Список підписників (тимчасово)"
