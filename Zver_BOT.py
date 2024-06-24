import asyncio
import types

from aiogram import Bot, Dispatcher, executor
from config import *
import logging, shutil
import plotly.graph_objects as go
from datetime import datetime as dt
from datetime import date
from log_in import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from checker_zakaz import parse_zakaz
import count_money
import parcel_manager
from money_manager import *
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from qr_give_mone import give_mobety_qr, quriers_money, get_data_money_city
from create_table_mount_money import *

from remain_sklad import calculate_stock_balance, count_stock

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

current_datetime = dt.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
source_db_path = DB_NAME + ".db"
backup_db_path = f'{DB_NAME}_{formatted_datetime}.db'

conn = sqlite3.connect(DB_NAME + ".db")
cursor = conn.cursor()
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS sklad_all (name TEXT,count INTEGER,"money"	INTEGER NOT NULL DEFAULT 0 )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS sklad_sr (name TEXT,count INTEGER )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS sklad_ul(name TEXT,count INTEGER )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS count_mai_sr(name TEXT,count INTEGER )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS count_mai_ul(name TEXT,count INTEGER )''')
conn.commit()

sklad_map = {
    -1001919781848: ("sklad_all", "Общие данные:\n"),
    -1001973484183: ("sklad_ul", "Данные Ульяновск:\n"),
    -1001875449260: ("sklad_sr", "Данные Саратов:\n"),
}
chart_map = {
    "/chart_all": ("sklad_all", "Общий склад:\n"),
    "/chart_ul": ("sklad_ul", "Склад Ульяновск:\n"),
    "/chart_sr": ("sklad_sr", "Склад Саратов:\n"),
}


@dp.message_handler(commands="erase_bd")
@auth
async def erase_bd(message: types.Message):
    ERASE_TEXT = f"""
    *Вы уверены, что хотите очистить данные?*
    *Будет создана копия: {backup_db_path}*
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    yes_button = InlineKeyboardButton("Да", callback_data="erase_confirm")
    no_button = InlineKeyboardButton("Нет", callback_data="erase_cancel")
    keyboard.add(yes_button, no_button)
    send_message = await message.reply(ERASE_TEXT, parse_mode='Markdown', reply_markup=keyboard)
    try:
        await asyncio.sleep(10)
        await bot.delete_message(chat_id=send_message.chat.id, message_id=send_message.message_id)
    except:
        pass


@dp.callback_query_handler(lambda c: c.data == 'erase_confirm')
async def confirm_erase(callback_query: CallbackQuery):
    shutil.copyfile(source_db_path, backup_db_path)
    cursor.execute("DELETE FROM sklad_all")
    cursor.execute("DELETE FROM sklad_sr")
    cursor.execute("DELETE FROM sklad_ul")
    cursor.execute("DELETE FROM count_mai_sr")
    cursor.execute("DELETE FROM count_mai_ul")
    cursor.execute("DELETE FROM Couriers")
    cursor.execute("DELETE FROM Delivery")
    cursor.execute("DELETE FROM Orders")
    # Orders Delivery Couriers
    conn.commit()
    ERASE_TEXT = f"""
    *Данные очищены!*
    *Копия: {backup_db_path}*
    """
    create_tables_and_insert_data()
    await bot.answer_callback_query(callback_query.id, text="Данные очищены")
    await bot.edit_message_text(ERASE_TEXT, callback_query.message.chat.id, callback_query.message.message_id,
                                parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'erase_cancel')
async def cancel_erase(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id, text="Очистка данных отменена")
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


async def mesg_del_time(msg_id: types.Message):
    await asyncio.sleep(15)
    await msg_id.delete()


async def btn_del_time(msg_id: types.Message):
    await asyncio.sleep(120)
    await msg_id.delete()


@dp.message_handler(commands=['info_count_mail'])
async def info_mail_handler(message):
    await parcel_manager.info_mail_handler(message)


@dp.message_handler(commands=['total_money'])
async def info_money_handler(message):
    await count_money.calculate_total(message)


@dp.message_handler(commands=['orders_money'])
async def info_order_money_handler(message):
    await order_money(message)


@dp.message_handler(commands=['delivery_money'])
async def info_delivery_money_handler(message):
    await delivery_money(message)


@dp.message_handler(commands=['couriers_money'])
async def info_сouriers_money_handler(message):
    await сouriers_money(message)


@dp.message_handler(commands=['giv_zp_qr'])
async def key_qr(message: types.Message, state: FSMContext):
    await message.delete()
    amounts = quriers_money()
    ulaynovsk_button = types.InlineKeyboardButton(text=f'Ульяновск: {amounts.get("UL", 0)} руб.',
                                                  callback_data='ulaynovsk')
    saratov_button = types.InlineKeyboardButton(text=f'Саратов: {amounts.get("SR", 0)} руб.', callback_data='saratov')
    inline_kb = types.InlineKeyboardMarkup(row_width=1)
    inline_kb.add(ulaynovsk_button, saratov_button)
    msg = await message.answer("Выберите город:", reply_markup=inline_kb)
    await state.finish()
    asyncio.create_task(btn_del_time(msg))


@dp.callback_query_handler(lambda callback_query: True)
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    if data == 'ulaynovsk' or data == 'saratov':
        city_name, city_amount, data_money = get_data_money_city(data)
        await state.set_state(data)
        msg = await bot.send_message(-1001919781848, f"Введите сумму для выдачи в: {city_name}\n"
                                                     f"Не более {city_amount} .руб\n"
                                                     f"Для отмены введите  - 0")
        asyncio.create_task(mesg_del_time(msg))


@dp.message_handler(state='ulaynovsk')
@dp.message_handler(state='saratov')
async def handle_amount(message: types.Message, state: FSMContext):
    data = await state.get_state()
    city_name, city_amount, courier_id = get_data_money_city(data)

    if data in ['ulaynovsk', 'saratov']:
        try:

            amount_to_money_data = message.text

            if amount_to_money_data.isdigit():

                amount_to_money = int(amount_to_money_data)

                if amount_to_money > city_amount:
                    msg = await message.answer(
                        f"Вы не можете выдать сумму больше,\nчем доступно для {city_name} ({city_amount} руб.)\n\n"
                        f"Для отмены введите  - 0")
                    asyncio.create_task(mesg_del_time(msg))

                    return
                await message.delete()
                give_money_city = city_amount - amount_to_money
                if amount_to_money == 0:
                    info_msg = f'Выдача {city_name} отменена'
                else:
                    info_msg = f'Баланс {city_name}: {give_money_city} .руб'
                    msg = await message.answer(f"Сумма {amount_to_money} .руб вычтена для города: {city_name}")
                    asyncio.create_task(mesg_del_time(msg))
                    give_mobety_qr(give_money_city, courier_id)

                msg = await message.answer(info_msg)
                asyncio.create_task(mesg_del_time(msg))
                await state.finish()

            else:
                msg = await message.answer("Только числовое значение, целое без точек и запятых")
                asyncio.create_task(mesg_del_time(msg))
        except ValueError:
            msg = await message.answer("Пожалуйста, введите корректное число")
            asyncio.create_task(mesg_del_time(msg))


@dp.message_handler(commands=['chart_all', 'chart_ul', 'chart_sr'])
async def show_chart(message: types.Message):
    chart = message.text
    if chart in chart_map:
        cgeo, cgeo_name = chart_map[chart]
    else:
        await message.reply("Неизвестная команда")
        return
    connection = sqlite3.connect("Sale.db")
    cursor = connection.cursor()
    query = f"SELECT name, count FROM {cgeo} ORDER BY count DESC"
    cursor.execute(query)
    results = cursor.fetchall()
    names = [f"{result[0]} ({result[1]}шт.)" for result in results]
    counts = [result[1] for result in results]
    fig = go.Figure(data=go.Bar(x=counts, y=names, orientation='h'))
    current_date = date.today().strftime("%d.%m.%Y")
    fig.update_layout(
        title=f"{cgeo_name} на {current_date}",
        xaxis_title="Количество",
        yaxis_title="Товар",
        width=1000,
        height=800,
        autosize=False
    )
    fig.write_html("my_chart.html")
    fig.write_image("my_chart.png")
    with open("my_chart.png", "rb") as chart_file:
        send_message = await message.answer_photo(chart_file)
    cursor.close()
    connection.close()
    await delmsg(send_message)
    await message.delete()


async def delmsg(send_message):
    TEXT_INF = """Какая-то тупица уже удалила сообщение...пошли вы нахуй, считайте сами!"""
    try:
        await asyncio.sleep(30)
        await bot.delete_message(chat_id=send_message.chat.id, message_id=send_message.message_id)
    except:
        del_msg = await bot.send_message(send_message.chat.id, text=TEXT_INF)
        await asyncio.sleep(10)
        await bot.delete_message(chat_id=del_msg.chat.id, message_id=del_msg.message_id)


@dp.message_handler(commands="help")
async def help(message: types.Message):
    HELP_TXT = """
*Список доступных команд:*
    1. */get_count_all - Общие данные*
    2. */get_count_ul - Ульяновск данные*
    3. */get_count_sr - Саратов данные*
    ----
    4. `/erase_bd` - стереть все данные (делает бэкап)
    ----
    5. */chart_all - Общая диаграмма*
    6. */chart_ul - Диаграмма Ульяновск*
    7. */chart_sr - Диаграмма Саратов*
    ----
    8. */info_count_mail - Статистика отправок*
    9. */giv_zp_qr - Выдать ЗП курьерам*
    ----
    10. */calk_stock - Остатки на складе*
    ----
    11. */total_money - Продано по прайсу(без учета скидок)*
    12. */delivery_money - Общая сумма денег за доставку*
    13. */couriers_money - Зарплата курьерам* 
    14. */orders_money - Общая сумма денег за заказы(с учетом всех скидок)*
    ----
    """
    send_message = await message.answer(HELP_TXT, parse_mode='Markdown')
    await delmsg(send_message)
    await message.delete()


@dp.message_handler(commands=["get_count_all", "get_count_ul", "get_count_sr"])
async def get_count_handler(message: types.Message):
    command = message.text
    command_map = {
        "/get_count_all": ("sklad_all", "Общие данные:\n"),
        "/get_count_ul": ("sklad_ul", "Данные Ульяновск:\n"),
        "/get_count_sr": ("sklad_sr", "Данные Саратов:\n"),
    }
    if command in command_map:
        geo, geo_name = command_map[command]
    else:
        await message.reply("Неизвестная команда")
        return
    cursor.execute(f"SELECT name, count FROM {geo} ORDER BY count DESC")
    rows = cursor.fetchall()
    if not rows:
        send_message = await message.reply("База данных пуста.")
    else:
        result = '\n'.join([f"{row[0]} х  {row[1]} шт." for row in rows])
        send_message = await message.reply(geo_name + "\n" + result)
    await delmsg(send_message)
    await message.delete()


@dp.message_handler(commands=["calk_stock"])
async def calk_stock(message: types.Message):
    await message.delete()
    calc = calculate_stock_balance()
    msg = await message.answer(f"{calc}")
    _ = asyncio.create_task(mesg_del_time(msg))


@dp.message_handler(content_types=types.ContentType.TEXT)
async def text_handler(message: types.Message):
    text = message.text

    await parse_zakaz(text)
    if message.chat.id == -1001919781848:
        await count_stock(text)

    chat_id = message['chat']['id']
    sklad_geo, sklad_name = sklad_map.get(chat_id)

    if sklad_geo == 'sklad_sr':
        parcel_manager.increase_mail_count_sklad_sr()
        await shopping_cart(message, 'SR')
    elif sklad_geo == 'sklad_ul':
        parcel_manager.increase_mail_count_sklad_ul()
        await shopping_cart(message, 'UL')

    pattern1 = r"Содержимое корзины:(.*?)(?=\n\n)"
    pattern2 = r"Содержимое корзины со скидкой:(.*?)(?=\n\n)"
    match = re.search(pattern1, text, re.DOTALL)
    if not match:
        match = re.search(pattern2, text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        items = re.findall(r"- (.+?) \(\d+ руб.\) x (\d+)", content)
        for item in items:
            name = item[0].strip()
            count = int(item[1].strip())
            cursor.execute(f"SELECT count FROM {sklad_geo} WHERE name = ?", (name,))
            result = cursor.fetchone()
            if result is not None:
                current_count = result[0]
                count += current_count
                cursor.execute(f"UPDATE {sklad_geo} SET count = ? WHERE name = ?", (count, name))
            else:
                cursor.execute(f"INSERT INTO {sklad_geo} (name, count) VALUES (?, ?)", (name, count))
        conn.commit()
        await get_sklad_geo(sklad_geo, sklad_name, message)
    else:
        send_message = await message.reply("Содержимое корзины не найдено.")
        await delmsg(send_message)


async def get_sklad_geo(sklad_geo, sklad_name, message):
    cursor.execute(f"SELECT name, count FROM {sklad_geo} ORDER BY count DESC")
    rows = cursor.fetchall()
    result = '\n'.join([f"{row[0]} х {row[1]} шт." for row in rows])
    send_message = await message.reply(f"{sklad_name}\n{result}")
    await delmsg(send_message)


def close_db():
    conn.close()


if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    finally:
        close_db()
