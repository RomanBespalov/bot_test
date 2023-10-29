from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from mailing.models import Profile

TOKEN = '6844289121:AAG7-QckQBvoQBCkrJHrU1OfLp3WlGc3hLo'


def registration(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    # user, _ = CustomUser.objects.get_or_create(
    #     user_id=chat_id,
    #     defaults={
    #         'name': update.message.from_user.username,
    #     }
    # )
    message_text = 'Регистрация прошла успешно'

    update.message.reply_text(f"Chat ID: {chat_id}\nMessage: {message_text}")


def main():

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, registration))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
