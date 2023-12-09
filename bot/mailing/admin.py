from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from mailing.models import (BroadcastMessage, Button, ButtonPress, Profile,
                            TemplateMessage)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user_id',
        'name',
        'is_blocked',
        'profile_info',
        'broadcast',
        'broadcast_display',
    )
    list_filter = ('is_blocked',)

    def is_blocked(self, obj):
        return 'Да' if obj.is_blocked else 'Нет'
    is_blocked.short_description = 'Статус блокировки'

    def broadcast_display(self, obj):
        broadcasts = BroadcastMessage.objects.filter(recipients=obj.id)
        text_list = [broadcast.text for broadcast in broadcasts]
        return ', '.join(text_list)
    broadcast_display.short_description = 'Текст рассылки'

    def profile_info(self, obj):
        link = format_html(
            '<a href="{}">Статистика по пользователю</a>',
            reverse('profile', args=[obj.name])
        )
        return link
    profile_info.short_description = 'Информация о пользователях'

    def broadcast(self, obj):
        url_1 = reverse('broadcast')
        return format_html('<a href="{}">Создать рассылку</a>', url_1)
    broadcast.short_description = 'Рассылки'


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    raw_id_fields = ('recipients',)

    def get_buttons_display(self, obj):
        return ', '.join([buttons.name for buttons in obj.buttons.all()])
    get_buttons_display.short_description = 'Кнопки'

    def get_recipients_display(self, obj):
        return ', '.join(
            [recipients.name for recipients in obj.recipients.all()]
        )
    get_recipients_display.short_description = 'Пользователи'

    def broadcast_statistic(sekf, obj):
        link = format_html(
            '<a href="{}">Статистика по рассылке</a>',
            reverse('broadcast_detail', args=[obj.id])
        )
        return link
    broadcast_statistic.short_description = 'Статистика по рассылке'

    list_display = (
        'name',
        'text',
        'get_buttons_display',
        'get_recipients_display',
        'broadcast_statistic',
    )
    list_filter = ('text',)


@admin.register(ButtonPress)
class ButtonPressAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'button',
        'count',
        'broadcast_message',
    )
    list_filter = ('button', 'user')


@admin.register(TemplateMessage)
class TemplateMessageAdmin(admin.ModelAdmin):

    def get_buttons_display(self, obj):
        return ', '.join([buttons.name for buttons in obj.buttons.all()])
    get_buttons_display.short_description = 'Кнопки'

    list_display = (
        'name',
        'text',
        'get_buttons_display',
    )
