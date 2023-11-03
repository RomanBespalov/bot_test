from django import forms

from mailing.models import BroadcastMessage, TemplateMessage


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


class TestBroadcastMessageForm(forms.ModelForm):
    class Meta:
        model = BroadcastMessage
        fields = ('name', 'text', 'buttons')
        labels = {
            'name': 'Название рассылки',
            'text': 'Текст рассылки',
            'buttons': 'Кнопки',
        }
        widgets = {
            'buttons': forms.CheckboxSelectMultiple,
        }


class TemplateMessageForm(forms.ModelForm):
    class Meta:
        model = TemplateMessage
        fields = ('name', 'text', 'buttons')
        labels = {
            'name': 'Название рассылки',
            'text': 'Текст рассылки',
            'buttons': 'Кнопки',
        }
        widgets = {
            'buttons': forms.CheckboxSelectMultiple,
        }
