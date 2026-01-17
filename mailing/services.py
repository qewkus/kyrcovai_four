from config.settings import CACHE_ENABLED, EMAIL_HOST_USER
from django.core.cache import cache
from django.core.mail import BadHeaderError, send_mail
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Mailing, MailingAttempt, Message, Recipient


def get_recipient_from_cache():
    """Получение данных из кеша, если кеш пуст, то получает данные из БД."""
    if not CACHE_ENABLED:
        return Recipient.objects.all()
    key = "recipients_list"
    recipient = cache.get(key)
    if recipient is not None:
        return recipient
    recipient = Recipient.objects.all()
    cache.set(key, recipient)
    return recipient


def get_mailing_from_cache():
    """Получает данные из кеша, если кеш пуст, то получает данные из БД."""
    if not CACHE_ENABLED:
        return Mailing.objects.all()
    key = "mailing_list"
    mailing = cache.get(key)
    if mailing is not None:
        return mailing
    mailing = Mailing.objects.all()
    cache.set(key, mailing)
    return mailing


def get_message_from_cache():
    """Получает данные из кеша, если кеш пуст, то получает данные из БД."""
    if not CACHE_ENABLED:
        return Message.objects.all()
    key = "message_list"
    message = cache.get(key)
    if message is not None:
        return message
    message = Message.objects.all()
    cache.set(key, message)
    return message


def send_mailing(mailing: Mailing = None):
    """Отправка рассылок. Обновлено под актуальную модель данных."""
    if not mailing:
        mailings_to_send = Mailing.objects.filter(
            Q(status="Создана") | Q(status="Запущена"),
            start_time__lte=timezone.now(),
        )
    else:
        mailings_to_send = [mailing]

    for mailing in mailings_to_send:
        mailing.status = "Запущена"
        mailing.start_time = timezone.now()

        with transaction.atomic():
            mailing.save()
            success_count = 0

            for recipient in mailing.recipients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body_of_the_letter,
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[recipient.email],
                    )

                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status="Успешно",
                        mail_server_response="Письмо отправлено успешно.",
                        date_time_of_attempt=timezone.now(),
                    )
                    success_count += 1

                except BadHeaderError as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status="Не успешно",
                        mail_server_response=str(e),
                        date_time_of_attempt=timezone.now(),
                    )
                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status="Не успешно",
                        mail_server_response=str(e),
                        date_time_of_attempt=timezone.now(),
                    )

            if success_count == mailing.recipients.count():
                mailing.status = "Завершена"
                mailing.end_time = timezone.now()

            mailing.save()
