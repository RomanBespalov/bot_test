from django import forms

from mailing.models import BroadcastMessage, TemplateMessage


class BroadcastMessageForm(forms.ModelForm):
    class Meta:
        model = BroadcastMessage
        fields = ('name', 'text', 'buttons', 'recipients', 'button_layout',)
        labels = {
            'name': 'Название рассылки',
            'text': 'Текст рассылки',
            'buttons': 'Кнопки',
            'recipients': 'Получатели',
            'button_layout': 'Расположение кнопок',
        }
        widgets = {
            'buttons': forms.CheckboxSelectMultiple,
            'recipients': forms.CheckboxSelectMultiple,
            'button_layout': forms.RadioSelect(choices=[(1, 'друг под другом'), (2, '2 кнопки рядом')]),
        }


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
