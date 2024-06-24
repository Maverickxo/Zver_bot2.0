import sqlite3
import asyncio
from datetime import date
DataBase = 'Sale.db'


def increase_mail_count_sklad_sr():
    with sqlite3.connect(DataBase) as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT count FROM count_mai_sr WHERE name=?', ('Saratov',))
        row = cursor.fetchone()

        if row is None:
            cursor.execute('''INSERT INTO count_mai_sr (name, count) VALUES (?, ?)''', ('Saratov', 1))
            new_mail_count = 1
        else:
            current_mail_count = row[0]
            new_mail_count = current_mail_count + 1
            cursor.execute('UPDATE count_mai_sr SET count = ? WHERE name = ?', (new_mail_count, 'Saratov'))

        connect.commit()
        return new_mail_count


def increase_mail_count_sklad_ul():
    with sqlite3.connect(DataBase) as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT count FROM count_mai_ul WHERE name=?', ('Ulyanovsk',))
        row = cursor.fetchone()

        if row is None:
            cursor.execute('''INSERT INTO count_mai_ul (name, count) VALUES (?, ?)''', ('Ulyanovsk', 1))
            new_mail_count = 1
        else:
            current_mail_count = row[0]
            new_mail_count = current_mail_count + 1
            cursor.execute('UPDATE count_mai_ul SET count = ? WHERE name = ?', (new_mail_count, 'Ulyanovsk'))

        connect.commit()
        return new_mail_count


def get_mail_count_data():
    with sqlite3.connect(DataBase) as connect:
        cursor = connect.cursor()

        cursor.execute('SELECT count FROM count_mai_sr WHERE name=?', ('Saratov',))
        saratov_row = cursor.fetchone()
        saratov_count = saratov_row[0] if saratov_row is not None else 0

        cursor.execute('SELECT count FROM count_mai_ul WHERE name=?', ('Ulyanovsk',))
        ulyanovsk_row = cursor.fetchone()
        ulyanovsk_count = ulyanovsk_row[0] if ulyanovsk_row is not None else 0

        total_count = saratov_count + ulyanovsk_count
        return saratov_count, ulyanovsk_count, total_count


async def info_mail_handler(message):
    cdate = date.today().strftime('%d.%m.%Y')
    saratov_count, ulyanovsk_count, total_count = get_mail_count_data()

    table = (
        "Склад        | Отправлено\n"
        "----------------------------\n"
        f"Саратов      | {saratov_count}\n"
        f"Ульяновск    | {ulyanovsk_count}\n"
        "----------------------------\n"
        f"Всего        | {total_count}"
    )
    msg = await message.answer(f'Статистика отправок {cdate}:\n\n```\n{table}\n```', parse_mode='Markdown')
    await asyncio.sleep(30)
    await message.delete()
    await msg.delete()