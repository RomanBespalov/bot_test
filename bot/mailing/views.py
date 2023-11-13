from django.shortcuts import render, redirect, get_object_or_404

from mailing.models import Profile, BroadcastMessage, Button, ButtonPress
from mailing.forms import BroadcastMessageForm
import asyncio
from mailing.send_from_bot import send_message
import json
from django.core.paginator import Paginator

ADMIN_CHAT_ID = 280305615


def broadcast(request):
    buttons = Button.objects.all()
    template = 'admin_custom/broadcast.html'

    if request.method == 'POST':
        form_data = request.POST.copy()

        selected_buttons_data = json.loads(
            form_data.get('selectedButtons', '[]')
        )
        form_data.update({'buttons': selected_buttons_data})
        form = BroadcastMessageForm(form_data, request.FILES)

        if form.is_valid():
            broadcast_message = form.save()

            message = form.cleaned_data['text']
            recipients = form.cleaned_data['recipients']
            buttons_instances = form.cleaned_data['buttons']

            broadcast_id = broadcast_message.id

            for recipient in recipients:
                chat_id = recipient.user_id
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    send_message(
                        chat_id, message, buttons_instances, broadcast_id
                    )
                )

            context = {
                'buttons': buttons,
                'form': form,
            }

            return render(request, template, context=context)
        else:
            print('Form is not valid:', form.errors)
    else:
        form = BroadcastMessageForm()

    context = {
            'buttons': buttons,
            'form': form,
        }
    return render(request, template, context)


def profile(request, name):
    user = get_object_or_404(Profile, name=name)
    posts = BroadcastMessage.objects.filter(recipients=user)
    buttons = ButtonPress.objects.filter(
        user=user, broadcast_message__in=posts
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'user': user,
        'posts': posts,
        'buttons': buttons,
    }
    return render(request, 'admin_custom/user_profile.html', context)


def broadcast_users(request):
    posts = BroadcastMessage.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin_custom/broadcast_users.html', context)


def telegram_bot_view(request):
    return redirect('https://t.me/vpn_yereven_bot')
