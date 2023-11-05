import asyncio
from telegram import Bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = '6844289121:AAG7-QckQBvoQBCkrJHrU1OfLp3WlGc3hLo'

bot = Bot(token=API_TOKEN)


async def send_message(chat_id, message, buttons, broadcast_id, row_width):
    whole_keyboard = []
    row = []
    for button in buttons:
        callback_data = f"{button.id}:{broadcast_id}"
        row.append(InlineKeyboardButton(button.name, callback_data=callback_data))
        if len(row) == row_width:
            whole_keyboard.append(row)
            row = []

    if row:
        whole_keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(whole_keyboard)

    bot.send_message(chat_id, message, reply_markup=reply_markup)
    return message

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message())
