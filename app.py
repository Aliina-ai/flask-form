import csv
import time
from telethon import TelegramClient, errors, functions
from telethon.tl.types import InputPhoneContact

# =========================
# Налаштування
# =========================
api_id = 28384371             # ваш api_id
api_hash = "8f3931fd2cdf0a1597c8a55b480f737c"    # ваш api_hash
sender_phone = "+380965829257" # номер вашого акаунта Telegram
invite_link = "https://t.me/BilaTserkvaToday"  # посилання на канал
csv_file = 'phones.csv'        # файл зі списком номерів
send_per_day = 20              # ліміт на день
pause_between_messages = 30    # секунда між повідомленнями

# Ваш текст запрошення:
message_text = """📢 Шановні мешканці та гості Білої Церкви!

Запрошуємо вас долучитися до Telegram-каналу “Біла Церква Сьогодні” – вашого надійного джерела актуальної інформації!

🔹 Оперативні новини міста та України
🔹 Корисні поради та цікаві факти
🔹 Анонси важливих подій і заходів
🔹 Атмосферні ранкові публікації

Будьте завжди в курсі подій, які формують життя нашого міста.
Підписуйтесь за посиланням:
👉 https://t.me/BilaTserkvaToday

Ми раді вітати вас у нашій спільноті!
"""


# =========================
# Підключення Telethon
# =========================
session_name = sender_phone.replace('+', '')  # назва файлу сесії
client = TelegramClient(session_name, api_id, api_hash)

async def main():
    await client.start(phone=sender_phone)
    print(f"Підключено як: {sender_phone}")

    # Зчитуємо номери
    phones = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                ph = row[0].strip()
                if ph:
                    phones.append(ph)

    # Завантажуємо лог тих, кому вже надіслали
    sent_log = 'sent_log.txt'
    sent = set()
    try:
        with open(sent_log, 'r', encoding='utf-8') as f:
            for line in f:
                sent.add(line.strip())
    except FileNotFoundError:
        pass

    # Вибираємо 20 нових номерів
    to_send = [p for p in phones if p not in sent][:send_per_day]

    for ph in to_send:
        try:
            contact = InputPhoneContact(client_id=0, phone=ph, first_name="Friend", last_name="")
            imported = await client(functions.contacts.ImportContactsRequest(contacts=[contact]))
            if not imported.users:
                print(f"✖ {ph} не знайдено в Telegram")
                continue
            user = imported.users[0]
            await client.send_message(user.id, message_text)
            print(f"✅ Надіслано {ph}")

            # Логуємо номер
            with open(sent_log, 'a', encoding='utf-8') as f:
                f.write(ph + "\n")

            time.sleep(pause_between_messages)
        except errors.FloodWaitError as e:
            print(f"⏸ Flood wait: {e.seconds} сек")
            time.sleep(e.seconds + 5)
        except Exception as e:
            print(f"⚠️ Помилка {ph}: {e}")
            continue

    print("🎯 Надсилання завершено")

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())

