from django.shortcuts import render, redirect

from mailing.models import Profile
from mailing.forms import BroadcastMessageForm
import asyncio
from mailing.send_from_bot import send_message


def user_info_view(request):
    users = Profile.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'user_info.html', context)


def broadcast_message_view(request):
    template = 'broadcast_message.html'

    if request.method == 'POST':
        form = BroadcastMessageForm(request.POST, request.FILES)
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
