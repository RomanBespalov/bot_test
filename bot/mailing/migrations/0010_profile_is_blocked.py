# Generated by Django 4.2.6 on 2023-11-16 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0009_button_row_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_blocked',
            field=models.BooleanField(blank=True, null=True, verbose_name='Статус блокировки'),
        ),
    ]
