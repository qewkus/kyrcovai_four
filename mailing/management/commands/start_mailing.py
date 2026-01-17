from django.core.management.base import BaseCommand
from mailing.models import Mailing


class Command(BaseCommand):
    help = "Начать рассылку"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Рассылка с ID {mailing_id} не найдена."))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Произошла непредвиденная ошибка: {str(e)}"))
            return

        if mailing.status != "Создана":
            self.stderr.write(self.style.ERROR(f'Рассылка с ID {mailing_id} не в статусе "Создана".'))
            return

        try:
            mailing.send_mailing()
            self.stdout.write(self.style.SUCCESS(f"Рассылка с ID {mailing_id} успешно начата."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при отправке рассылки: {str(e)}"))
