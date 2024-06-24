import sqlite3
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types


def qiers_money():
    conn = sqlite3.connect('Sale.db')
    curs = conn.cursor()
    curs.execute('SELECT product_name, sklad FROM stock_balance  ')
    data = curs.fetchall()
    amounts = {row[0]: row[1] for row in data} if data else {}

    conn.close()
    return amounts


print(qiers_money())


async def next_map_server(message: types.Message):
    # await message.delete()
    key = qiers_money()

    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text=map_name, callback_data=f'choose_map_{map_name}')
        for map_name in key
    ]
    inline_keyboard.add(*buttons)
    print(buttons)
    await message.answer("Склад", reply_markup=inline_keyboard)


