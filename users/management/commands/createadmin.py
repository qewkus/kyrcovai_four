from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from config.settings import EMAIL_ADMIN, PASSWORD_ADMIN


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.create(email=EMAIL_ADMIN, first_name="admin", last_name="admin")

        user.set_password(PASSWORD_ADMIN)
        user.is_staff = True
        user.is_superuser = True

        user.save()

        self.stdout.write(self.style.SUCCESS(f"Суперпользователь с email {user.email}, успешно создан."))
