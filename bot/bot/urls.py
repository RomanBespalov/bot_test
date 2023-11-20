from django.contrib import admin
from django.urls import path

from mailing import views

urlpatterns = [
    path('admin/broadcast_detail/<int:broadcast_id>/', views.broadcast_detail, name='broadcast_detail'),
    path('admin/broadcast_statistic/', views.broadcast_statistic, name='broadcast_statistic'),
    path(
        'admin/choose_users/',
        views.choose_users,
        name='choose_users'
    ),
    path(
        'admin/broadcast/broadcast_users/',
        views.broadcast_users,
        name='broadcast_users'
    ),
    path('admin/broadcast/', views.broadcast, name='broadcast'),
    path('admin/profile/<str:name>/', views.profile, name='profile'),
    path('admin/', admin.site.urls),
    path('', views.telegram_bot_view, name='telegram_bot',)
]
