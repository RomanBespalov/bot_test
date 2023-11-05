# Generated by Django 4.2.6 on 2023-11-04 22:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0005_buttonpress_broadcast_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buttonpress',
            name='broadcast_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='button_press_user', to='mailing.broadcastmessage', verbose_name='Рассылка'),
        ),
    ]
