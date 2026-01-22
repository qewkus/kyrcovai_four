from django import forms

from mailing.models import Mailing, Message, Recipient


class RecipientForm(forms.ModelForm):
    """Класс формы клиента"""

    class Meta:
        model = Recipient
        fields = ["full_name", "email", "comment"]


class MessageForm(forms.ModelForm):
    """Класс формы сообщения"""

    class Meta:
        model = Message
        fields = ["subject", "body_of_the_letter", "owner"]
        widgets = {
            "body_of_the_letter": forms.Textarea(attrs={"placeholder": "Введите сообщение..."}),
        }


class MailingForm(forms.ModelForm):
    """Класс формы для рассылки"""

    class Meta:
        model = Mailing
        fields = ["message", "recipients", "status"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_authenticated:
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)
            self.fields["message"].queryset = Message.objects.filter(owner=user)
        else:
            self.fields["recipients"].queryset = Recipient.objects.none()
            self.fields["message"].queryset = Message.objects.none()
