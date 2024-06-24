import sqlite3
from aiogram import types
from price import *
import asyncio

async def calculate_total(message: types.Message):
    await message.delete()
    update_prices_based_on_dict()

    connect = sqlite3.connect('Sale.db')
    curs = connect.cursor()
    money = curs.execute('SELECT * FROM sklad_all').fetchall()

    products = []
    for row in money:
        name = row[0]
        count = row[1]
        price = row[2]
        result_money = count * price
        products.append((name, count, result_money))
    sorted_products = sorted(products, key=lambda x: x[2], reverse=True)
    tovar_list = []
    for name, count, result_money in sorted_products:
        product_info = f"{name}: |{count}шт.| >>> {result_money} руб.\n"
        print(product_info)
        tovar_list.append(product_info)
    total_cost = sum(result_money for _, _, result_money in sorted_products)
    total_info = f'\nОбщая стоимость: {round(total_cost)} руб.'
    print(total_info)
    tovar_list.append(total_info)
    formatted_tovar_list = '\n'.join(tovar_list)
    msg = await message.answer(formatted_tovar_list)
    await asyncio.sleep(30)
    await msg.delete()


def update_prices_based_on_dict():
    connect = sqlite3.connect('Sale.db')
    curs = connect.cursor()
    for name, price in prices.items():
        existing_product = curs.execute('SELECT name, money FROM sklad_all WHERE name = ?', (name,)).fetchone()

        if existing_product:
            existing_money = existing_product[1]
            if existing_money == 0:
                curs.execute('UPDATE sklad_all SET money = ? WHERE name = ?', (price, name))
                connect.commit()
                print(f"Цена для товара '{name}' добавлена: {price} руб.")

    connect.close()

