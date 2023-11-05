from django.shortcuts import render, redirect, get_object_or_404

from mailing.models import Profile, BroadcastMessage, Button, ButtonPress
from mailing.forms import BroadcastMessageForm, TestBroadcastMessageForm, TemplateMessageForm
import asyncio
from mailing.send_from_bot import send_message


ADMIN_CHAT_ID = 280305615


def profile(request, name):
    user = get_object_or_404(Profile, name=name)
    posts = BroadcastMessage.objects.filter(recipients=user)
    buttons = ButtonPress.objects.filter(user=user, broadcast_message__in=posts)
    # page_obj = pagination(request, posts_profile_list)
    context = {
        # 'page_obj': page_obj,
        'user': user,
        'posts': posts,
        'buttons': buttons,
    }
    return render(request, 'admin_custom/user_profile.html', context)


def broadcast_message_view(request):
    template = 'admin_custom/broadcast_message.html'

    if request.method == 'POST':
        if 'template' in request.POST:
            form = TemplateMessageForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                context = {
                    'form': form,
                }
                return render(request, template, context)
            form = TemplateMessageForm(request.POST, request.FILES)
        if 'test_broadcast' in request.POST:
            form = TestBroadcastMessageForm(request.POST, request.FILES)
            if form.is_valid():
                message = form.cleaned_data['text']
                buttons = form.cleaned_data['buttons']
                chat_id = ADMIN_CHAT_ID
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_message(chat_id, message, buttons))
                context = {
                    'form': form,
                }
                return render(request, template, context)
            form = TestBroadcastMessageForm(request.POST, request.FILES)
        form = BroadcastMessageForm(request.POST, request.FILES)
        if form.is_valid():
            broadcast_message = form.save()
            message = form.cleaned_data['text']
            recipients = form.cleaned_data['recipients']
            buttons = form.cleaned_data['buttons']
            broadcast_id = broadcast_message.id
            button_layout = form.cleaned_data['button_layout']
            print(button_layout)
            for recipient in recipients:
                chat_id = recipient.user_id
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_message(chat_id, message, buttons, broadcast_id, button_layout))
            context = {
                'form': form,
            }
            return render(request, template, context)
    else:
        form = BroadcastMessageForm()

    context = {
        'form': form,
    }

    return render(request, template, context)


def telegram_bot_view(request):
    return redirect('https://t.me/vpn_yereven_bot')
