from django.db import models


class Profile(models.Model):
    """Модель пользователей."""
    user_id = models.PositiveIntegerField(
        verbose_name='ID пользователя в телеграмм',
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Имя пользователя',
        blank=True,
        null=True,
    )
    is_blocked = models.BooleanField(
        verbose_name='Статус блокировки',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Button(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название кнопки',
        blank=True,
        null=True,
    )
    data = models.JSONField(
        verbose_name='JSON-данные кнопки',
        help_text='JSON-данные кнопки, включая текст и стили',
        blank=True,
        null=True,
    )
    row_number = models.IntegerField(
        verbose_name='номер строки',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Кнопка'
        verbose_name_plural = 'Кнопки'
        ordering = ['-id']

    def __str__(self):
        return self.name


class BroadcastMessage(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='название рассылки',
    )
    text = models.TextField(
        verbose_name='текст рассылки',
    )
    buttons = models.ManyToManyField(
        Button,
        verbose_name='кнопки для ответа на рассылку',
        related_name='broadcast_buttons',
    )
    recipients = models.ManyToManyField(
        Profile,
        verbose_name='получатели',
        related_name='recipients',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата отправки',
        db_index=True,
    )
    button_layout = models.IntegerField(
        verbose_name='Расположение кнопок',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Отправленная Рассылка'
        verbose_name_plural = 'Отправленные Рассылки'
        ordering = ['-id']

    def __str__(self):
        return self.name


class TemplateMessage(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='название шаблона',
    )
    text = models.TextField(
        verbose_name='текст шаблона',
    )
    buttons = models.ManyToManyField(
        Button,
        verbose_name='кнопки для ответа на рассылку',
        related_name='template_buttons',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Шаблон рассылки'
        verbose_name_plural = 'Шаблоны рассылок'
        ordering = ['-id']

    def __str__(self):
        return self.name


class ButtonPress(models.Model):
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='button_presses',
        verbose_name='Пользователь',
    )
    button = models.ForeignKey(
        Button,
        on_delete=models.CASCADE,
        related_name='button_presses',
        verbose_name='Кнопка',
    )
    broadcast_message = models.ForeignKey(
        BroadcastMessage,
        on_delete=models.CASCADE,
        related_name='button_press_user',
        verbose_name='Рассылка',
        blank=True,
        null=True,
    )
    count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество нажатий',
    )

    class Meta:
        verbose_name = 'Статистика по кликами'
        verbose_name_plural = 'Статистика по кликами'
        ordering = ['-id']

    def __str__(self):
        return f'{ self.user.name } нажал на { self.button.name } { self.count } раз'
