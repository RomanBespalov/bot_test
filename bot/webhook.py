import os

import django
from telegram import Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Updater)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
django.setup()

from mailing.models import Profile, Button, ButtonPress, BroadcastMessage
from django.http import JsonResponse

TOKEN = '6844289121:AAG7-QckQBvoQBCkrJHrU1OfLp3WlGc3hLo'
NGROK_URL = 'https://2878-178-160-197-197.ngrok-free.app'

from django.views.decorators.csrf import csrf_exempt
import json
updater = Updater(token=TOKEN, use_context=True)

def new(request, *args, **kwargs):
    print('new')

@csrf_exempt
def set_webhook():
    print('webhook')
    bot = updater.bot
    bot.setWebhook(url=f'{NGROK_URL}/webhook/')


# def registration(update: Update, context: CallbackContext):
#     chat_id = update.message.chat.id
#     Profile.objects.get_or_create(
#         user_id=chat_id,
#         defaults={
#             'name': update.message.from_user.username,
#         }
#     )
#     Profile.objects.filter(user_id=chat_id).first()
#     message_text = 'Регистрация прошла успешно'
#     user_name = update.effective_user

#     update.message.reply_text(
#         f"Привет, {user_name.first_name}!\n"
#         f"Chat ID: {chat_id}\n{message_text}"
#     )


@csrf_exempt
def button_callback(request, *args, **kwargs):
    print('Зашли в функцию callback')
    if request.method == 'POST':
        json_str = request.body.decode('UTF-8')
        data = json.loads(json_str)

        # Создаем объект Update
        update = Update.de_json(data, bot=updater.bot)
        query = update.callback_query
        button_id = int(query.data.split(':')[0])
        broadcast_id = int(query.data.split(':')[1])
        user_id = update.effective_user.id

        button = Button.objects.get(id=button_id)
        user = Profile.objects.get(user_id=user_id)
        broadcast = BroadcastMessage.objects.get(id=broadcast_id)
        button_press, _ = ButtonPress.objects.get_or_create(
            user=user, button=button, broadcast_message=broadcast
        )
        button_press.count += 1
        button_press.save()

        query.answer(f"Вы нажали на кнопку {button.name} {button_press.count} раз")

        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def main():
    print('1')
    dispatcher = updater.dispatcher

    # dispatcher.add_handler(CommandHandler('start', registration))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    updater.start_webhook(
        listen="0.0.0.0",
        port=8000,
        url_path="/webhook/",
        webhook_url=f"{NGROK_URL}/webhook/",
    )
    updater.idle()


if __name__ == '__main__':
    print('2')
    set_webhook()
    main()
