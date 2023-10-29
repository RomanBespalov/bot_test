import asyncio
from telegram import Bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = '6844289121:AAG7-QckQBvoQBCkrJHrU1OfLp3WlGc3hLo'

bot = Bot(token=API_TOKEN)


async def send_message(chat_id, message, buttons):
    whole_keyboard = []
    for button in buttons:

        keyboard = [InlineKeyboardButton(button.name, callback_data='button_click')]
        whole_keyboard.append(keyboard)
        reply_markup = InlineKeyboardMarkup(whole_keyboard)

    bot.send_message(chat_id, message, reply_markup=reply_markup)
    return message

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message())
