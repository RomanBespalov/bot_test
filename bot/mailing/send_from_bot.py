import asyncio

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup


API_TOKEN = '6844289121:AAG7-QckQBvoQBCkrJHrU1OfLp3WlGc3hLo'
bot = Bot(token=API_TOKEN)


async def send_message(chat_id, message, buttons_instances, broadcast_id):
    keyboard_dict = {}

    for button in buttons_instances:
        line = button.row_number
        button_id = button.id
        if broadcast_id is None:
            callback_data = f"{button_id}:{line}"
        else:
            callback_data = f"{button_id}:{broadcast_id}:{line}"

        if line not in keyboard_dict:
            keyboard_dict[line] = []

        keyboard_dict[line].append(
            InlineKeyboardButton(button.name, callback_data=callback_data)
        )

    sorted_keyboard = sorted(keyboard_dict.items(), key=lambda x: int(x[0]))
    reply_markup = InlineKeyboardMarkup(
        [[button for button in row] for _, row in sorted_keyboard]
    )
    bot.send_message(chat_id, message, reply_markup=reply_markup)
    return message

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message())
