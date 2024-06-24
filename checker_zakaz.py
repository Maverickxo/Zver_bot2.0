import re
import datetime
from connect_db import connect_data_b


async def parse_zakaz(text):
    """Поиск номера заказа"""
    nomer_zakaza = r'№(\d+)'
    data = datetime.datetime.today().strftime("%d.%m.%Y - %H:%M")
    matches = re.search(nomer_zakaza, text)
    if matches:
        order_number = matches.group(1)
        print("Номер заказа:", order_number)
        await insert_zakaz(order_number, data)
    else:
        print("Номер заказа не найден")


async def insert_zakaz(order_number, order_date):
    """Проверка заказа и вставка в базу данных"""
    connection, cursor = connect_data_b()
    cursor.execute('SELECT zakaz FROM zakaz WHERE zakaz = %s', (order_number,))
    exi_zakaz = cursor.fetchone()
    if not exi_zakaz:
        cursor.execute("INSERT INTO zakaz (zakaz, data) VALUES (%s, %s)", (order_number, order_date,))
    cursor.close()
    connection.close()

