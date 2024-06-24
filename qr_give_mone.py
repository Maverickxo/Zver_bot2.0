from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3


def give_mobety_qr(courier_amount, courier_id):
    with sqlite3.connect('Sale.db') as conn:
        curs = conn.cursor()
        curs.execute("UPDATE Couriers SET courier_amount = ? WHERE courier_id = ?", (courier_amount, courier_id))
        conn.commit()
        curs.close()


def quriers_money():
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute('SELECT courier_id, courier_amount FROM Couriers WHERE courier_id IN ("UL", "SR")')
    data = curs.fetchall()
    amounts = {row[0]: row[1] for row in data} if data else {}
    conn.close()
    return amounts


def get_data_money_city(data):
    amounts = quriers_money()
    city_name = "Ульяновск" if data == 'ulaynovsk' else "Саратов"
    data_money = "UL" if data == "ulaynovsk" else "SR"
    city_amount = amounts.get(data_money, 0)
    return city_name, city_amount, data_money
