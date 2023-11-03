from django.shortcuts import render, redirect

from mailing.models import Profile
from mailing.forms import BroadcastMessageForm, TestBroadcastMessageForm, TemplateMessageForm
import asyncio
from mailing.send_from_bot import send_message


ADMIN_CHAT_ID = 280305615


def user_info_view(request):
    users = Profile.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'index.html', context)


def broadcast_message_view(request):
    template = 'broadcast_message.html'

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
        if form.is_valid():
            form.save()
            message = form.cleaned_data['text']
            recipients = form.cleaned_data['recipients']
            buttons = form.cleaned_data['buttons']
            for recipient in recipients:
                chat_id = recipient.user_id
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_message(chat_id, message, buttons))
            return redirect('broadcast_message')
    else:
        form = BroadcastMessageForm()

    context = {
        'form': form,
    }

    return render(request, template, context)
