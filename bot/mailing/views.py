from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse

from mailing.models import Profile, BroadcastMessage, Button, ButtonPress, TemplateMessage
from mailing.forms import BroadcastMessageForm, RecipientsForm, TestBroadcastMessageForm, TemplateMessageForm
import asyncio
from mailing.send_from_bot import send_message
import json
from django.core.paginator import Paginator


ADMIN_CHAT_ID = 280305615


def broadcast(request):
    # temps = TemplateMessage.objects.all()
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

    context = {
        'buttons': buttons,
        'form': form,
        # 'temps': temps,
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
        # if 'template_filter' in request.POST:
        #     template = request.POST['template_filter']
        #     if template != '':
        #         template_1 = TemplateMessage.objects.filter(name__icontains=template)

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
            if 'selected_user_ids' not in request.session or not request.session['selected_user_ids']:
                request.session['selected_user_ids'] = user_ids
            else:
                request.session['selected_user_ids'] += user_ids
                request.session['selected_user_ids'] = list(set(request.session['selected_user_ids']))
            print(request.session['selected_user_ids'])
            return redirect(reverse('broadcast_users'))
        else:
            return render(request, 'admin_custom/close_window.html')
    elif request.method == 'GET':
        # Очистка данных в сессии при сбросе фильтров
        request.session.pop('selected_user_ids', None)
        return redirect(reverse('broadcast_users'))


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
    flag = True
    broadcast = get_object_or_404(BroadcastMessage, id=broadcast_id)
    users = broadcast.recipients.all()

    paginator = Paginator(users, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    users_on_page = page_obj.object_list
    user_buttons_dict = {}

    if 'blocked' in request.POST:
        recipients = Profile.objects.filter(is_blocked=True)
        for user in recipients:
            if BroadcastMessage.objects.filter(recipients=user, id=broadcast_id):
                buttons = ButtonPress.objects.filter(user=user, broadcast_message=broadcast)
                user_buttons_dict[user] = buttons, user.is_blocked
        blocked = True
        context = {
            'blocked': blocked,
            'broadcast': broadcast,
            'user_buttons_dict': user_buttons_dict,
            'flag': user_buttons_dict,
        }
        return render(request, 'admin_custom/broadcast_detail.html', context)

    if 'not_blocked' in request.POST:
        recipients = Profile.objects.filter(is_blocked=False)
        for user in recipients:
            if BroadcastMessage.objects.filter(recipients=user, id=broadcast_id):
                buttons = ButtonPress.objects.filter(user=user, broadcast_message=broadcast)
                user_buttons_dict[user] = buttons, user.is_blocked
        not_blocked = True
        context = {
            'not_blocked': not_blocked,
            'broadcast': broadcast,
            'user_buttons_dict': user_buttons_dict,
            'flag': user_buttons_dict,
        }
        return render(request, 'admin_custom/broadcast_detail.html', context)

    if 'button_filter' in request.POST and request.POST['button_filter'] != '':
        filtered_users = []
        button_name = request.POST['button_filter']
        buttons = Button.objects.filter(name__icontains=button_name)
        butts = []
        for button in buttons:
            buttons_pressed = ButtonPress.objects.filter(button=button, broadcast_message=broadcast)
            if buttons_pressed:
                for button_pressed in buttons_pressed:
                    filtered_users.append(button_pressed.user)
                    butts.append(button_pressed.button.name)

        filtered_users = list(set(filtered_users))
        for user in filtered_users:
            buttons = ButtonPress.objects.filter(user=user, broadcast_message=broadcast)
            user_buttons_dict[user] = buttons, user.is_blocked
        context = {
            'butts': butts,
            'broadcast': broadcast,
            'filtered_users': filtered_users,
            'user_buttons_dict': user_buttons_dict,
            'flag': filtered_users,
        }
        return render(request, 'admin_custom/broadcast_detail.html', context)

    for user in users_on_page:
        buttons = ButtonPress.objects.filter(user=user, broadcast_message=broadcast)
        user_buttons_dict[user] = buttons, user.is_blocked

    context = {
        'broadcast': broadcast,
        'user_buttons_dict': user_buttons_dict,
        'flag': flag,
    }
    return render(request, 'admin_custom/broadcast_detail.html', context)


def broadcast_templates(request):
    if request.method == 'POST':
        if 'submit' in request.POST:
            template_id = request.POST.get('selected_template')
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
    paginator = Paginator(templates, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin_custom/templates.html', context)
