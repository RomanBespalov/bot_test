# Generated by Django 4.2.6 on 2023-11-02 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0003_alter_broadcastmessage_options_alter_button_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broadcastmessage',
            name='buttons',
            field=models.ManyToManyField(related_name='broadcast_buttons', to='mailing.button', verbose_name='кнопки для ответа на рассылку'),
        ),
        migrations.CreateModel(
            name='TemplateMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='название шаблона')),
                ('text', models.TextField(verbose_name='текст шаблона')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='дата создания')),
                ('buttons', models.ManyToManyField(related_name='template_buttons', to='mailing.button', verbose_name='кнопки для ответа на рассылку')),
            ],
            options={
                'verbose_name': 'Шаблон рассылки',
                'verbose_name_plural': 'Шаблоны рассылок',
                'ordering': ['-id'],
            },
        ),
    ]