from django.contrib import admin

from .models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "comment")
    list_filter = ("full_name",)
    search_fields = (
        "email",
        "full_name",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "body_of_the_letter")
    list_filter = ("subject",)
    search_fields = (
        "subject",
        "body_of_the_letter",
    )


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_time",
        "end_time",
        "status",
        "message",
    )
    list_filter = ("status",)
    search_fields = ("status",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "date_time_of_attempt", "status", "mail_server_response", "mailing")
    list_filter = ("status",)
    search_fields = ("status",)
