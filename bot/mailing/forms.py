from django import forms
from django.db.models import Case, When
from django.utils.safestring import mark_safe

from mailing.models import BroadcastMessage, Button, Profile, TemplateMessage


class RecipientsRawIdWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        return mark_safe(
            f'{html}<a href="#" onclick="showRecipientsPopup()">Выбрать</a>'
        )


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
            'name': 'Название рассылки:',
            'text': 'Текст рассылки:',
            'buttons': 'Кнопки',
            'recipients': 'Получатели',
        }

    def __init__(self, *args, **kwargs):
        super(BroadcastMessageForm, self).__init__(*args, **kwargs)

        self.fields['buttons'].required = False

    def clean_buttons(self):
        buttons_data = self.cleaned_data.get('buttons', [])
        if buttons_data is None:
            buttons_instances = []
            return buttons_instances

        button_info = [
            (int(button['name'][-1]), button['value'])
            for button in buttons_data if 'value' in button
        ]

        buttons_dict = {
            str(button_value): str(row_number)
            for row_number, button_value in button_info
        }

        buttons_instances = Button.objects.filter(
            id__in=buttons_dict.keys()
        ).order_by(Case(*[
            When(id=id_val, then=pos) for pos, id_val in enumerate(
                buttons_dict.keys()
            )
        ], default=None))

        for button_instance in buttons_instances:
            button_instance.row_number = buttons_dict.get(
                str(button_instance.id), None
            )
            button_instance.save()

        return buttons_instances

    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']
        return [profile.id for profile in recipients]


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
