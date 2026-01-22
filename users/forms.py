from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text="Необязательное поле. Введите номер телефона, состоящий только из цифр.",
    )
    username = forms.CharField(max_length=50, required=False)

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "avatar", "username", "phone_number", "password1", "password2")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")

        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр.")
        return phone_number

    def clean_avatar(self):
        cleaned_data = super().clean()
        avatar = cleaned_data.get("avatar")

        if avatar is None:
            return None

        max_size = 5 * 1024 * 1024
        if avatar.size > max_size:
            raise forms.ValidationError("Размер файла превышает 5 MB.")
        if not avatar.name.lower().endswith((".jpg", ".jpeg", ".png")):
            raise forms.ValidationError(
                "Формат файла не поддерживается. Допустимый формат файла: *.jpg, *.jpeg, *.png"
            )
        return avatar

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Пользователь с именем {username} уже существует")
        return username
