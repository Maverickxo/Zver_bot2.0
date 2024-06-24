import sqlite3


def create_tables_and_insert_data():
    try:
        conn = sqlite3.connect('Sale.db')
        cursor = conn.cursor()

        # Создаем таблицу деньги за заказы
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS "Orders" ("order_id" INTEGER,"order_amount" INTEGER,PRIMARY KEY("order_id"))''')

        # Создаем таблицу деньги за доставку
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS "Delivery" ("delivery_id" INTEGER,"delivery_amount" INTEGER,PRIMARY KEY("delivery_id")) ''')

        # Создаем таблицу деньги курьерам
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS "Couriers" ("courier_id" TEXT,"courier_amount" INTEGER,PRIMARY KEY("courier_id"))''')

        # Добавляем запись в таблицу деньги за заказы
        cursor.execute('''INSERT INTO Orders (order_id, order_amount)VALUES (1, 0)''')

        # Добавляем запись в таблицу деньги за доставку
        cursor.execute('''INSERT INTO Delivery (delivery_id, delivery_amount)VALUES (1, 0)''')

        # Добавляем запись в таблицу деньги курьерам
        cursor.executemany('''INSERT INTO Couriers (courier_id, courier_amount) VALUES (?, 0)''', [("UL",), ("SR",)])

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("An error occurred:", e)



