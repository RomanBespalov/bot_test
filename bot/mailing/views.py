from django.shortcuts import render, redirect, get_object_or_404

from mailing.models import Profile, BroadcastMessage, Button, ButtonPress
from mailing.forms import BroadcastMessageForm, RecipientsForm, TestBroadcastMessageForm, TemplateMessageForm
import asyncio
from mailing.send_from_bot import send_message
import json
from django.core.paginator import Paginator


ADMIN_CHAT_ID = 280305615


def broadcast(request):
    buttons = Button.objects.all()
    template = 'admin_custom/broadcast.html'
    clicked_button = request.POST.get('clickedButton', None)

    if request.method == 'POST':
        form_data = request.POST.copy()
        selected_buttons_data = json.loads(
            form_data.get('selectedButtons', '[]')
        )
        form_data.update({
                'buttons': selected_buttons_data,
            })

        if clicked_button == 'test_broadcast':
            form = TestBroadcastMessageForm(form_data)
            if form.is_valid():
                message = form.cleaned_data['text']
                buttons_instances = form.cleaned_data['buttons']
                broadcast_id = None
                chat_id = ADMIN_CHAT_ID
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    send_message(
                        chat_id, message, buttons_instances, broadcast_id
                    )
                )
        elif clicked_button == 'template':
            form = TemplateMessageForm(request.POST)
            if form.is_valid():
                form.save()

        elif clicked_button == 'create':
            selected_user_ids = request.session.get('selected_user_ids', [])
            form_data.setlist('recipients', selected_user_ids)
            form = BroadcastMessageForm(form_data, request.FILES)

            if form.is_valid():
                broadcast_message = form.save()

                message = form.cleaned_data['text']
                recipients = form.cleaned_data['recipients']
                buttons_instances = form.cleaned_data['buttons']
                broadcast_id = broadcast_message.id

                for user_id in recipients:
                    recipient = get_object_or_404(Profile, id=user_id)
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
                del request.session['selected_user_ids']
                return render(request, template, context=context)

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
    if request.method == 'POST':
        output = []
        if 'username_filter' in request.POST:
            user_name = request.POST['username_filter']
            if user_name != '':
                output = Profile.objects.filter(name__icontains=user_name)

        if 'broadcast_filter' in request.POST:
            message = request.POST['broadcast_filter']
            if message != '':
                broadcast = BroadcastMessage.objects.filter(name__icontains=message)
                for mailing in broadcast:
                    user = mailing.recipients.all()
                    for us in user:
                        output.append(us)
            output = list(set(output))
        if 'button_filter' in request.POST:
            button_name = request.POST['button_filter']
            if button_name != '':
                buttons = Button.objects.filter(name__icontains=button_name)
                for button in buttons:
                    button_presses = ButtonPress.objects.filter(button=button.id)
                    for buttonpress in button_presses:
                        output.append(buttonpress.user)
                output = list(set(output))

        if 'blocked' in request.POST:
            output = Profile.objects.filter(is_blocked=True)
        if 'not_blocked' in request.POST:
            output = Profile.objects.filter(is_blocked=False)
        return render(request, 'admin_custom/broadcast_users.html', {'output': output})
    if request.method == 'GET':
        users = Profile.objects.all()
        paginator = Paginator(users, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'admin_custom/broadcast_users.html', context)


def telegram_bot_view(request):
    return redirect('https://t.me/vpn_yereven_bot')


def choose_users(request):
    if request.method == 'POST':
        form = RecipientsForm(request.POST)

        if form.is_valid():
            selected_users = form.cleaned_data['selected_users']
            user_ids = [int(user.id) for user in selected_users]
            request.session['selected_user_ids'] = user_ids
            return render(request, 'admin_custom/close_window.html')


def broadcast_statistic(request):
    broadcast = BroadcastMessage.objects.all()
    paginator = Paginator(broadcast, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin_custom/broadcast_statistic.html', context)


def broadcast_detail(request, broadcast_id):
    broadcast = get_object_or_404(BroadcastMessage, id=broadcast_id)
    users = broadcast.recipients.all()
    paginator = Paginator(users, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    users_on_page = page_obj.object_list

    user_buttons_dict = {}
    for user in users_on_page:
        buttons = ButtonPress.objects.filter(user=user, broadcast_message=broadcast)
        user_buttons_dict[user] = buttons, user.is_blocked

    context = {
        'page_obj': page_obj,
        'broadcast': broadcast,
        'user_buttons_dict': user_buttons_dict,
    }
    return render(request, 'admin_custom/broadcast_detail.html', context)
