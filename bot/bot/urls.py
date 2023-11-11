from django.contrib import admin
from django.urls import path

from mailing import views

urlpatterns = [
    path('admin/button/', views.button, name='button'),
    path('admin/profile/<str:name>/', views.profile, name='profile'),
    path(
        'admin/broadcast_message/',
        views.broadcast_message_view,
        name='broadcast_message',
    ),
    path('admin/', admin.site.urls),
    path(
        'https://t.me/vpn_yereven_bot',
        views.telegram_bot_view,
        name='telegram_bot',)
]
