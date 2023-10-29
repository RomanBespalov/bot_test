from django.db import models


class Profile(models.Model):
    """Модель пользователей."""
    user_id = models.PositiveIntegerField(
        verbose_name='ID пользователя',
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Имя пользователя',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

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
        verbose_name='Данные кнопки',
        help_text='JSON-данные кнопки, включая текст и стили',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Кнопку'
        verbose_name_plural = 'Кнопки'
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
    count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество нажатий',
    )


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
        related_name='buttons',
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

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-id']

    def __str__(self):
        return self.name
