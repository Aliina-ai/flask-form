import sqlite3

# Створення або підключення до файлу бази даних
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Створення таблиці elders, якщо вона ще не існує
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

print("✅ Базу даних успішно створено — файл 'database.db' тепер існує.")
