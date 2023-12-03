import asyncio
import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from mailing.forms import (BroadcastMessageForm, RecipientsForm,
                           TemplateMessageForm)
from mailing.models import (BroadcastMessage, Button, ButtonPress, Profile,
                            TemplateMessage)
from mailing.send_from_bot import send_message


def pagination(request, body):
    paginator = Paginator(body, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def broadcast(request):
    if 'broadcast_template_data' in request.session:
        temp = request.session['broadcast_template_data']

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

        if clicked_button == 'template':
            form = TemplateMessageForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({'valid': True})
            else:
                return JsonResponse({'valid': False})

        elif clicked_button == 'create' or clicked_button == 'test_broadcast':
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
                if clicked_button == 'create':
                    del request.session['selected_user_ids']
                return render(request, template, context=context)

    else:
        if 'broadcast_template_data' in request.session:
            initial_data = {
                'name': temp['name'],
                'text': temp['text'],
            }

            form = BroadcastMessageForm(initial=initial_data)
            del request.session['broadcast_template_data']
            context = {
                'buttons': buttons,
                'form': form,
            }
            return render(request, template, context)
        else:
            form = BroadcastMessageForm()
    if 'selected_user_ids' in request.session:
        del request.session['selected_user_ids']
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
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'user': user,
        'posts': posts,
        'buttons': buttons,
    }
    return render(request, 'admin_custom/user_profile.html', context)


flag_user, flag_broadcast, flag_button, flag_blocked, flag_not_blocked = 5*[False]


def broadcast_users(request):
    output = []
    global flag_user
    global flag_broadcast
    global flag_button
    global flag_blocked
    global flag_not_blocked

    if 'reset' in request.POST:
        request.session.pop('selected_user_ids', None)
        if 'username_filter' in request.session:
            request.session.pop('username_filter', None)
            flag_user = False
        if 'broadcast_filter' in request.session:
            request.session.pop('broadcast_filter', None)
            flag_broadcast = False
        if 'button_filter' in request.session:
            request.session.pop('button_filter', None)
            flag_button = False
        flag_blocked = False
        flag_not_blocked = False

        return redirect(reverse('broadcast_users'))

    if 'username_filter' in request.POST and request.POST['username_filter'] != '' or flag_user is True:
        if flag_user is False:
            users_name = request.POST['username_filter']
            request.session['username_filter'] = users_name
            output = Profile.objects.filter(name__icontains=users_name)
            page_obj = pagination(request, output)
            context = {
                'page_obj': page_obj,
            }
            flag_user = True
            return render(request, 'admin_custom/broadcast_users.html', context)
        else:
            output = Profile.objects.filter(name__icontains=request.session['username_filter'])
            page_obj = pagination(request, output)
            context = {
                'page_obj': page_obj,
            }
            if 'select_all' in request.POST:
                user_ids = [int(user.id) for user in output]
                request.session['selected_user_ids'] = user_ids
            return render(request, 'admin_custom/broadcast_users.html', context)

    if 'broadcast_filter' in request.POST and request.POST['broadcast_filter'] != '' or flag_broadcast is True:
        if flag_broadcast is False:
            message = request.POST['broadcast_filter']
            request.session['broadcast_filter'] = message
            broadcast = BroadcastMessage.objects.filter(
                name__icontains=message
            )
            for mailing in broadcast:
                user = mailing.recipients.all()
                for us in user:
                    output.append(us)
            output = list(set(output))
            page_obj = pagination(request, output)
            context = {
                'page_obj': page_obj,
            }
            flag_broadcast = True
            return render(request, 'admin_custom/broadcast_users.html', context)
        else:
            broadcast = BroadcastMessage.objects.filter(
                name__icontains=request.session['broadcast_filter']
            )
            for mailing in broadcast:
                user = mailing.recipients.all()
                for us in user:
                    output.append(us)
            output = list(set(output))
            page_obj = pagination(request, output)
            context = {
                'page_obj': page_obj,
            }
            if 'select_all' in request.POST:
                user_ids = [int(user.id) for user in output]
                request.session['selected_user_ids'] = user_ids
            return render(request, 'admin_custom/broadcast_users.html', context)

    if 'button_filter' in request.POST and request.POST['button_filter'] != '' or flag_button is True:
        if flag_button is False:
            button_name = request.POST['button_filter']
            request.session['button_filter'] = button_name
            buttons = Button.objects.filter(name__icontains=button_name)
            for button in buttons:
                buttons_press = ButtonPress.objects.filter(
                    button=button.id
                )
                for button_press in buttons_press:
                    output.append(button_press.user)
            output = list(set(output))
            page_obj = pagination(request, output)
            context = {
                'page_obj': page_obj,
            }
            flag_button = True
            return render(request, 'admin_custom/broadcast_users.html', context)
        else:
            buttons = Button.objects.filter(name__icontains=request.session['button_filter'])
            for button in buttons:
                button_presses = ButtonPress.objects.filter(
                    button=button.id
                )
                for buttonpress in button_presses:
                    output.append(buttonpress.user)
            output = list(set(output))
            page_obj = pagination(request, output)
            context = {
                'page_obj': page_obj,
            }
            if 'select_all' in request.POST:
                user_ids = [int(user.id) for user in output]
                request.session['selected_user_ids'] = user_ids
            return render(request, 'admin_custom/broadcast_users.html', context)

    if 'blocked' in request.POST or flag_blocked is True:
        flag_blocked = True
        blocked_users = Profile.objects.filter(is_blocked=True)
        page_obj = pagination(request, blocked_users)
        context = {
                'page_obj': page_obj,
            }
        if 'select_all' in request.POST:
            user_ids = [int(user.id) for user in blocked_users]
            request.session['selected_user_ids'] = user_ids
        return render(request, 'admin_custom/broadcast_users.html', context)

    if 'not_blocked' in request.POST or flag_not_blocked is True:
        flag_not_blocked = True
        not_blocked_users = Profile.objects.filter(is_blocked=False)
        page_obj = pagination(request, not_blocked_users)
        context = {
            'page_obj': page_obj,
        }
        if 'select_all' in request.POST:
            user_ids = [int(user.id) for user in not_blocked_users]
            request.session['selected_user_ids'] = user_ids
        return render(request, 'admin_custom/broadcast_users.html', context)

    if request.method == 'GET':
        users = Profile.objects.all()
        page_obj = pagination(request, users)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'admin_custom/broadcast_users.html', context)
    return redirect(reverse('broadcast_users'))


def telegram_bot_view(request):
    return redirect('https://t.me/vpn_yereven_bot')


def choose_users(request):
    if request.method == 'POST':
        form = RecipientsForm(request.POST)

        if form.is_valid():
            selected_users = form.cleaned_data['selected_users']
            user_ids = [int(user.id) for user in selected_users]
            if ('selected_user_ids' not in request.session or
               not request.session['selected_user_ids']):
                request.session['selected_user_ids'] = user_ids
            else:
                request.session['selected_user_ids'] += user_ids
                request.session['selected_user_ids'] = list(
                    set(request.session['selected_user_ids'])
                )
            return redirect(reverse('broadcast_users'))
        else:
            return render(request, 'admin_custom/close_window.html')
    elif request.method == 'GET':
        request.session.pop('selected_user_ids', None)
        return redirect(reverse('broadcast_users'))


def broadcast_detail(request, broadcast_id):
    global flag_button
    global flag_blocked
    global flag_not_blocked

    flag = False
    broadcast = get_object_or_404(BroadcastMessage, id=broadcast_id)
    users = broadcast.recipients.all()
    all_buttons = broadcast.buttons.all()

    page_obj = pagination(request, users)
    output = []

    users_on_page = page_obj.object_list
    user_buttons_dict = {}

    if 'reset' in request.POST:
        if 'button_filter' in request.session:
            request.session.pop('button_filter', None)
            flag_button = False
        flag_blocked = False
        flag_not_blocked = False

    if 'blocked' in request.POST or flag_blocked is True:
        flag_blocked = True
        blocked_users = []
        for user in users:
            if user.is_blocked is True:
                blocked_users.append(user)

        page_obj = pagination(request, blocked_users)
        users_on_page = page_obj.object_list

        for user in users_on_page:
            buttons = ButtonPress.objects.filter(
                user=user, broadcast_message=broadcast
            )
            user_buttons_dict[user] = buttons, user.is_blocked

        blocked = True
        context = {
            'page_obj': page_obj,
            'blocked': blocked,
            'broadcast': broadcast,
            'user_buttons_dict': user_buttons_dict,
            'all_buttons': all_buttons,
        }
        return render(request, 'admin_custom/broadcast_detail.html', context)

    if 'not_blocked' in request.POST or flag_not_blocked is True:
        flag_not_blocked = True
        not_blocked_users = []
        for user in users:
            if user.is_blocked is False:
                not_blocked_users.append(user)

        page_obj = pagination(request, not_blocked_users)
        users_on_page = page_obj.object_list

        for user in users_on_page:
            buttons = ButtonPress.objects.filter(
                user=user, broadcast_message=broadcast
            )
            user_buttons_dict[user] = buttons, user.is_blocked

        not_blocked = True
        context = {
            'page_obj': page_obj,
            'not_blocked': not_blocked,
            'broadcast': broadcast,
            'user_buttons_dict': user_buttons_dict,
            'all_buttons': all_buttons,
        }
        return render(request, 'admin_custom/broadcast_detail.html', context)

    if 'button_filter' in request.POST and request.POST['button_filter'] != '' or flag_button is True:
        if flag_button is False:
            button_name = request.POST['button_filter']
            request.session['button_filter'] = button_name
            buttons = Button.objects.filter(name__icontains=button_name)
            for button in buttons:
                buttons_press = ButtonPress.objects.filter(
                    button=button.id
                )
                for button_press in buttons_press:
                    output.append(button_press.user)
            output = list(set(output))
            page_obj = pagination(request, output)
            users_on_page = page_obj.object_list

            for user in users_on_page:
                buttons = ButtonPress.objects.filter(
                    user=user, broadcast_message=broadcast
                )
                user_buttons_dict[user] = buttons, user.is_blocked

            context = {
                'page_obj': page_obj,
                'broadcast': broadcast,
                'user_buttons_dict': user_buttons_dict,
                'flag': True,
                'all_buttons': all_buttons,
            }
            flag_button = True
            return render(request, 'admin_custom/broadcast_detail.html', context)
        else:
            buttons = Button.objects.filter(name__icontains=request.session['button_filter'])
            for button in buttons:
                buttons_press = ButtonPress.objects.filter(
                    button=button.id
                )
                for button_press in buttons_press:
                    output.append(button_press.user)
            output = list(set(output))
            page_obj = pagination(request, output)
            users_on_page = page_obj.object_list

            for user in users_on_page:
                buttons = ButtonPress.objects.filter(
                    user=user, broadcast_message=broadcast
                )
                user_buttons_dict[user] = buttons, user.is_blocked

            context = {
                'page_obj': page_obj,
                'broadcast': broadcast,
                'user_buttons_dict': user_buttons_dict,
                'flag': True,
                'all_buttons': all_buttons,
            }
            return render(request, 'admin_custom/broadcast_detail.html', context)

    for user in users_on_page:
        buttons = ButtonPress.objects.filter(
            user=user, broadcast_message=broadcast
        )
        user_buttons_dict[user] = buttons, user.is_blocked

    context = {
        'page_obj': page_obj,
        'broadcast': broadcast,
        'user_buttons_dict': user_buttons_dict,
        'flag': flag,
        'all_buttons': all_buttons,
    }
    return render(request, 'admin_custom/broadcast_detail.html', context)


def broadcast_templates(request):
    if request.method == 'POST':
        if 'submit' in request.POST:
            template_id = request.POST.get('selected_template')
            if template_id is None:
                return render(request, 'admin_custom/close_window.html')
            template = get_object_or_404(TemplateMessage, id=template_id)
            initial_data = {
                'name': template.name,
                'text': template.text,
            }

            form = BroadcastMessageForm(initial=initial_data)

            context = {
                'form': form,
            }
            request.session['broadcast_template_data'] = {
                'name': template.name,
                'text': template.text,
            }
            return render(request, 'admin_custom/close_window.html')

    templates = TemplateMessage.objects.all()
    page_obj = pagination(request, templates)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin_custom/templates.html', context)
