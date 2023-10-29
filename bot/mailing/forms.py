from django import forms

from mailing.models import BroadcastMessage


class BroadcastMessageForm(forms.ModelForm):
    class Meta:
        model = BroadcastMessage
        fields = ('name', 'text', 'buttons', 'recipients')
        labels = {
            'name': 'Название рассылки',
            'text': 'Текст рассылки',
            'buttons': 'Кнопки',
            'recipients': 'Получатели',
        }
        widgets = {
            'buttons': forms.CheckboxSelectMultiple,
            'recipients': forms.CheckboxSelectMultiple,
        }
        select_all_recipients = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'select-all-checkbox'}))
