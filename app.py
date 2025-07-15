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
        pickup_points_list = request.form.getlist('pickup_points')
        pickup_points = ', '.join(pickup_points_list)

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO big_districts (
                    district_number, last_name, first_name, middle_name, phone, pickup_points
                ) VALUES (?, ?, ?, ?, ?, ?)
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

# Запуск додатку
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
