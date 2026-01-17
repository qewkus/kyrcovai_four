import json

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда для создания фикстуры групп пользователей"""

    def handle(self, *args, **options):
        groups = Group.objects.all()
        group_data = []

        for group in groups:
            group_data.append(
                {
                    "model": "auth.group",
                    "pk": group.id,
                    "fields": {
                        "name": group.name,
                        "permissions": [perm.id for perm in group.permissions.all()],
                    },
                }
            )

        with open("group_fixture.json", "w", encoding="utf-8") as f:
            json.dump(group_data, f, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS("Файл group_fixture.json успешно создан"))