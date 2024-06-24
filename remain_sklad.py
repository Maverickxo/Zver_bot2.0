import sqlite3
import re


async def count_stock(message):
    connection = sqlite3.connect('Sale.db')
    cursor = connection.cursor()

    pattern1 = r"Содержимое корзины:(.*?)(?=\n\n)"
    pattern2 = r"Содержимое корзины со скидкой:(.*?)(?=\n\n)"
    match = re.search(pattern1, message, re.DOTALL)
    if not match:
        match = re.search(pattern2, message, re.DOTALL)
    if match:
        content = match.group(1).strip()
        items = re.findall(r"- (.+?) \(\d+ руб.\) x (\d+)", content)
        for item in items:
            name = item[0].strip()
            count = int(item[1].strip())

            cursor.execute('SELECT * FROM stock_balance WHERE product_name=?', (name,))
            item = cursor.fetchone()

            if item:
                print('На складе всего:', item[1], 'шт.', item[2])
                res = item[2] - count
                print('После продажи', res)
                cursor.execute('UPDATE stock_balance SET sklad = ? WHERE product_name = ?', (res, name))

    connection.commit()
    cursor.close()


def calculate_stock_balance():
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute("SELECT * FROM stock_balance")
    data = curs.fetchall()
    result = ""
    entry_count = 1
    for row in data:
        result += f'{entry_count}. |{row[1]}| остаток: {row[2]} шт. \n'
        entry_count += 1
    print(result)
    return result


def duplicate_product_names():
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute('SELECT name FROM sklad_all')
    product_names = curs.fetchall()
    for product_name in product_names:
        curs.execute('SELECT COUNT(*) FROM stock_balance WHERE product_name = ?', (product_name[0],))
        count = curs.fetchone()[0]
        if count == 0:
            curs.execute('INSERT INTO stock_balance (product_name) VALUES (?)', (product_name[0],))

    conn.commit()
    conn.close()
