from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from mailing.forms import MailingForm, MessageForm, RecipientForm
from mailing.mixins import OwnerRequiredMixin
from mailing.services import get_mailing_from_cache, get_message_from_cache, get_recipient_from_cache, send_mailing

from .models import Mailing, MailingAttempt, Message, Recipient


class HomeView(ListView):
    model = Mailing
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["all_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(
            status="Запущена",
        ).count()
        context["unique_recipients"] = Recipient.objects.values_list("email", flat=True).distinct().count()

        return context


class RecipientListView(ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_perm("can_view_mailings_of_all_recipients"):
            return Recipient.objects.all()
        else:
            user = self.request.user
            return Recipient.objects.filter(owner=user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_create.html"
    success_url = reverse_lazy("mailing:home")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(OwnerRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_create.html"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientDeleteView(OwnerRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.has_perm("mailing.recipient_delete")
            or self.request.user.owner
        )

    def handle_no_permission(self):
        return redirect("mailing:recipient_list")


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class MessageListView(ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_perm("can_view_all_message"):
            return get_message_from_cache()
        else:
            user = self.request.user
            return Message.objects.filter(owner=user)


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_create.html"
    success_url = reverse_lazy("mailing:home")

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(OwnerRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_create.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(OwnerRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.message.owner
            and self.request.user.has_perm("mailing.message_delete")
        )

    def handle_no_permission(self):
        return redirect("mailing:message_list")


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


class MailingListView(ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_perm("can_view_mailings_of_all_recipients"):
            return get_mailing_from_cache()

        else:
            return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_create.html"
    success_url = reverse_lazy("mailing:home")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingUpdateView(OwnerRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_create.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(OwnerRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.has_perm("mailing.mailing_delete")
            or self.request.mailing.owner
        )

    def handle_no_permission(self):
        return redirect("mailing:mailing_list")

    def get_object(self, queryset=None):
        return get_object_or_404(Mailing, pk=self.kwargs["pk"])


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"


class SendMailingView(View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        response = send_mailing(mailing)
        return render(request, "mailing_detail.html", {"mailing": mailing, "response": response})


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = "mailing/attempt_list.html"
    context_object_name = "attempt_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(mailing__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["attempts_count"] = queryset.count()
        context["attempts_success_count"] = queryset.filter(status="Успешно").count()
        context["attempts_error_count"] = queryset.filter(status="Не успешно").count()
        return context


class BlockMailingView(LoginRequiredMixin, View):

    def get(self, request, mailing_id):
        mailing = get_object_or_404(Mailing, id=mailing_id)
        return render(request, "mailing/mailing_block.html", {"mailing": mailing})

    def post(self, request, mailing_id):
        mailing = get_object_or_404(Mailing, id=mailing_id)

        if not request.user.has_perm("mailing.can_block_mailings"):
            return HttpResponseForbidden("У вас нет прав для блокировки рассылки.")

        mailing.is_block = not mailing.is_block

        mailing.status = "Блокирована" if mailing.status != "Блокирована" else "Создана"
        mailing.save()

        return redirect("mailing:attempt_list")
