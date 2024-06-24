import re
import sqlite3
from aiogram import types
import asyncio
from mount_dostavka import extract_values_delivery



async def order_money(message: types.Message):
    '''Общая сумма денег за заказы'''
    await message.delete()
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute('SELECT order_amount FROM Orders WHERE order_id = 1')
    data = curs.fetchone()[0]
    conn.commit()
    conn.close()
    msg = await message.answer(f'`Общая сумма денег за заказы\n(с учетом всех скидок): {data}руб.`',
                               parse_mode='markdown')
    await asyncio.sleep(30)
    await msg.delete()


async def delivery_money(message: types.Message):
    '''Деньги за доставку'''
    await message.delete()
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute('SELECT delivery_amount FROM Delivery WHERE delivery_id = 1')
    data = curs.fetchone()[0]
    conn.commit()
    conn.close()
    msg = await message.answer(f'`Общая сумма денег за доставку: {data}руб.`', parse_mode='markdown')
    await asyncio.sleep(30)
    await msg.delete()


async def сouriers_money(message: types.Message):
    '''Деньги курьерам'''
    await message.delete()
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute('SELECT courier_amount FROM Couriers WHERE courier_id = "UL"')
    ulaynovsk = curs.fetchone()[0]
    curs.execute('SELECT courier_amount FROM Couriers WHERE courier_id = "SR"')
    saratov = curs.fetchone()[0]
    conn.commit()
    conn.close()
    msg = await message.answer(f'Зарплата Курьерам:\n\n`Ульяновск: {ulaynovsk}руб.\nСаратов: {saratov}руб.`',
                               parse_mode='markdown')
    await asyncio.sleep(30)
    await msg.delete()


def pars_summa_Delivery(count):
    '''Сумма доставки: '''
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute(
        '''CREATE TABLE IF NOT EXISTS Delivery ("delivery_id" INTEGER PRIMARY KEY,"delivery_amount" INTEGER NOT NULL DEFAULT 0)''')
    curs.execute("SELECT delivery_amount FROM Delivery WHERE delivery_id = 1")
    existing_count = curs.fetchone()
    if existing_count is not None:
        updated_count = existing_count[0] + count
        curs.execute("UPDATE Delivery SET delivery_amount = ? WHERE delivery_id = 1", (updated_count,))
    else:
        curs.execute("INSERT INTO Delivery (delivery_id, delivery_amount) VALUES (1, ?)", (count,))
    conn.commit()
    conn.close()


def pars_summa_k_oplate(count):
    '''Сумма к оплате: '''
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute(
        '''CREATE TABLE IF NOT EXISTS Orders ("order_id" INTEGER PRIMARY KEY,"order_amount" INTEGER NOT NULL DEFAULT 0)''')
    curs.execute("SELECT order_amount FROM Orders WHERE order_id = 1")
    existing_count = curs.fetchone()
    if existing_count is not None:
        updated_count = existing_count[0] + count
        curs.execute("UPDATE Orders SET order_amount = ? WHERE order_id = 1", (updated_count,))
    else:
        curs.execute("INSERT INTO Orders (order_id, order_amount) VALUES (1, ?)", (count,))
    conn.commit()
    conn.close()


def money_couriers(amount, courier_id):
    '''зарплата курьерам'''
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute(
        '''CREATE TABLE IF NOT EXISTS "Couriers" ("courier_id" TEXT,"courier_amount" INTEGER,PRIMARY KEY("courier_id"))''')
    curs.execute("SELECT courier_id, courier_amount FROM Couriers WHERE courier_id = ?", (courier_id,))
    existing_data = curs.fetchone()
    if existing_data is not None:
        existing_count = existing_data[1]
        updated_count = existing_count + amount
        curs.execute("UPDATE Couriers SET courier_amount = ? WHERE courier_id = ?", (updated_count, courier_id))
    else:
        print('Ошибка запроса ЗП')
    conn.commit()
    conn.close()


async def shopping_cart(message: types.Message, courier_id):
    '''Парсинг корзины'''
    message_zakaz = message.text
    dostavka_amount = extract_values_delivery(message_zakaz)  # TODO: сменить функцию расчета зп курьерам
    match = re.search(r'Сумма к оплате: (\d+) руб.', message_zakaz)
    if match:
        amount_to_pay = int(match.group(1))  # Сумма к оплате
        kur_money = dostavka_amount - 300  # Деньги курьеру за доставку

        pars_summa_k_oplate(amount_to_pay)
        money_couriers(kur_money, courier_id)
        pars_summa_Delivery(dostavka_amount)

        print(f'Сумма к оплате: {amount_to_pay}')
        print(f'Стоимость доставки: {dostavka_amount}')
        print(f'Денег курьеру: {kur_money}')

        msg = await message.answer(f'В счет ЗП: +{kur_money} .руб')
        await asyncio.sleep(15)
        await msg.delete()
    else:
        await message.answer("Сумма к оплате не найдена.")
