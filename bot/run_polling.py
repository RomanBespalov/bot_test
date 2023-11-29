import os

import django
from telegram import Update
from telegram.ext import Updater, CallbackContext, CallbackQueryHandler, CommandHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from mailing.models import Profile, Button, ButtonPress, BroadcastMessage


TOKEN = '6844289121:AAG7-QckQBvoQBCkrJHrU1OfLp3WlGc3hLo'


def registration(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    Profile.objects.get_or_create(
        user_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    Profile.objects.filter(user_id=chat_id).first()
    message_text = 'Регистрация прошла успешно'
    user_name = update.effective_user

    update.message.reply_text(
        f"Привет, {user_name.first_name}!\n"
        f"Chat ID: {chat_id}\n{message_text}"
    )


def button_callback(update, context):
    query = update.callback_query
    button_id = int(query.data.split(':')[0])
    broadcast_id = int(query.data.split(':')[1])
    user_id = update.effective_user.id

    button = Button.objects.get(id=button_id)
    user = Profile.objects.get(user_id=user_id)
    broadcast = BroadcastMessage.objects.get(id=broadcast_id)
    button_press, _ = ButtonPress.objects.get_or_create(user=user, button=button, broadcast_message=broadcast)
    button_press.count += 1
    button_press.save()

    query.answer(f"Вы нажали на кнопку '{button.name}' ({button_press.count} раз)")


def main():

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', registration))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
