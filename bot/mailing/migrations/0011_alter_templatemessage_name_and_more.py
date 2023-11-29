# Generated by Django 4.2.6 on 2023-11-29 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0010_profile_is_blocked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatemessage',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='название шаблона'),
        ),
        migrations.AlterField(
            model_name='templatemessage',
            name='text',
            field=models.TextField(unique=True, verbose_name='текст шаблона'),
        ),
    ]
