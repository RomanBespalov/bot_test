from django.contrib import admin
from django.urls import path

from mailing import views

urlpatterns = [
    path(
        'admin/user_info/',
        views.user_info_view,
        name='user_info',
    ),
    path(
        'admin/broadcast_message/',
        views.broadcast_message_view,
        name='broadcast_message',
    ),
    path('admin/', admin.site.urls),
]
