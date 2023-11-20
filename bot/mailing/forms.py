from django import forms
from django.db.models import Case, When

from mailing.models import BroadcastMessage, TemplateMessage, Button, Profile
from django.utils.safestring import mark_safe


class RecipientsRawIdWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        return mark_safe(f'{html}<a href="#" onclick="showRecipientsPopup()">Выбрать</a>')


class BroadcastMessageForm(forms.ModelForm):
    buttons = forms.JSONField(required=False)

    recipients = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all(),
        widget=RecipientsRawIdWidget,
        required=False,
        label='Пользователи',
    )

    class Meta:
        model = BroadcastMessage
        fields = ('name', 'text', 'buttons', 'recipients')
        labels = {
            'name': 'Название рассылки',
            'text': 'Текст рассылки',
            'buttons': 'Кнопки',
            'recipients': 'Получатели',
        }

    def __init__(self, *args, **kwargs):
        super(BroadcastMessageForm, self).__init__(*args, **kwargs)

        self.fields['buttons'].required = False

    def clean_buttons(self):
        buttons_data = self.cleaned_data.get('buttons', [])

        # Извлекаем последнюю цифру из имени и значение из каждой кнопки
        button_info = [(int(button['name'][-1]), button['value']) for button in buttons_data if 'value' in button]

        # Создаем словарь, где ключ - id кнопки, значение - строка
        buttons_dict = {str(button_value): str(row_number) for row_number, button_value in button_info}

        # Получаем экземпляры модели Button по их id
        buttons_instances = Button.objects.filter(id__in=buttons_dict.keys()).order_by(
            Case(*[When(id=id_val, then=pos) for pos, id_val in enumerate(buttons_dict.keys())], default=None)
        )

        # Обновляем данные в базе данных, устанавливая row_number
        for button_instance in buttons_instances:
            # Используем button_instance.id в качестве ключа
            button_instance.row_number = buttons_dict.get(str(button_instance.id), None)
            button_instance.save()

        return buttons_instances

    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']
        return [profile.id for profile in recipients]


class TestBroadcastMessageForm(BroadcastMessageForm):

    class Meta:
        model = BroadcastMessage
        fields = ('name', 'text', 'buttons')

    def __init__(self, *args, **kwargs):
        super(TestBroadcastMessageForm, self).__init__(*args, **kwargs)
        self.fields.pop('recipients')


class TemplateMessageForm(forms.ModelForm):
    class Meta:
        model = TemplateMessage
        fields = ('name', 'text')
        labels = {
            'name': 'Название рассылки',
            'text': 'Текст рассылки',
        }


class RecipientsForm(forms.Form):
    selected_users = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
