def auth(func):
    async def wrapper(message):
        if message['from']['id'] not in [5869013585, 6086279292]:
            return await message.reply("Доступ запрещен", reply=False)
        return await func(message)
    return wrapper


