from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from mailing.models import Profile, BroadcastMessage, Button


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user_id',
        'name',
        'user_info_link',
        'broadcast_message_link',
    )
    # list_filter = ('is_blocked',)

    # def is_blocked(self, obj):
    #     return 'Да' if obj.is_blocked else 'Нет'
    # is_blocked.short_description = 'Статус блокировки'

    def user_info_link(self, obj):
        url = reverse('user_info')
        return format_html('<a href="{}">Посмотреть статистику</a>', url)
    user_info_link.short_description = 'Информация о пользователях'

    def broadcast_message_link(self, obj):
        url = reverse('broadcast_message')
        return format_html('<a href="{}">Создать рассылку</a>', url)
    broadcast_message_link.short_description = 'Рассылки'


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'data',
    )


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'text',
        # 'buttons',
        # 'recipients',
    )
