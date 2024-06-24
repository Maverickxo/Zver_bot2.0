from aiogram import types



# def auth(func):
#     async def wrapper(message):
#         if message['from']['id'] != 5869013585:
#             return await message.reply("Доступ запрещен", reply=False)
#         return await func(message)
#     return wrapper


# def aut_cgt():
#     def decorator(func):
#         async def wrapper(message: types.Message):
#             if message.chat.type != types.ChatType.PRIVATE:
#                 await message.reply("Пожалуйста, отправляйте сообщения боту только в приватных чатах.")
#                 return
#             return await func(message)
#         return wrapper
#     return decorator


def auth_chat(func):
    async def wrapper(message):
        chat_id = message['chat']['id']  # Получаем идентификатор чата из сообщения
        allowed_chat_ids = [-1001768677683]  # Список разрешённых идентификаторов чатов
        if chat_id not in allowed_chat_ids:
            send = await message.reply("Доступ только в боте! !", reply=False)
            await asyncio.sleep(3)
            await bot.delete_message(chat_id=send.chat.id, message_id=send.message_id)
        return await func(message)
    return wrapper
#

#
# def auth(func):
#     async def wrapper(message):
#         if message['from']['id'] not in [5869013585]:
#             return await message.reply("Доступ запрещен", reply=False)
#         return await func(message)
#     return wrapper
#
#
# import asyncio
#
#
# def auth_chat(func):
#     async def wrapper(message):
#         chat_id = message['chat']['id']  # Получаем идентификатор чата из сообщения
#         allowed_chat_ids = [6156241028]  # Список разрешённых идентификаторов чатов
#
#         if chat_id not in allowed_chat_ids:
#             send = await message.reply("Доступ только в боте!", reply=False)
#             await asyncio.sleep(3)
#             await message.bot.delete_message(chat_id=send.chat.id, message_id=send.message_id)
#             return
#
#         return await func(message)
#
#     return wrapper

