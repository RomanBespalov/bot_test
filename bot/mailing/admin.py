from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from mailing.models import Profile, BroadcastMessage, Button, ButtonPress, TemplateMessage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user_id',
        'name',
        'user_info_link',
        'broadcast_message_link',
        'get_broadcast_message_display',
    )
    # list_filter = ('is_blocked',)

    # def is_blocked(self, obj):
    #     return 'Да' if obj.is_blocked else 'Нет'
    # is_blocked.short_description = 'Статус блокировки'

    def get_broadcast_message_display(self, obj):
        broadcasts = BroadcastMessage.objects.filter(recipients=obj.id)
        text_list = [broadcast.text for broadcast in broadcasts]
        return ', '.join(text_list)
    get_broadcast_message_display.short_description = 'Текст рассылки'

    def user_info_link(self, obj):
        link = format_html('<a href="{}">Посмотреть статистику</a>', reverse('profile', args=[obj.name]))
        return link
    user_info_link.short_description = 'Информация о пользователях'

    def broadcast_message_link(self, obj):
        url = reverse('broadcast_message')
        return format_html('<a href="{}">Создать рассылку</a>', url)
    broadcast_message_link.short_description = 'Рассылки'


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'data',
    )


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):

    def get_buttons_display(self, obj):
        return ', '.join([buttons.name for buttons in obj.buttons.all()])
    get_buttons_display.short_description = 'Кнопки'

    def get_recipients_display(self, obj):
        return ', '.join([recipients.name for recipients in obj.recipients.all()])
    get_recipients_display.short_description = 'Пользователи'

    list_display = (
        'name',
        'text',
        'get_buttons_display',
        'get_recipients_display',
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
    list_filter = ('button',)


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
