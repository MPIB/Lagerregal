from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from mail.models import MailTemplate, MailTemplateRecipient
from mail.forms import MailTemplateForm
from users.models import Lageruser
from Lagerregal.utils import PaginationMixin


class MailList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = MailTemplate
    context_object_name = 'mail_list'
    permission_required = 'mail.read_mailtemplate'

    def get_queryset(self):
        return MailTemplate.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates"))]

        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class MailDetail(PermissionRequiredMixin, DetailView):
    model = MailTemplate
    context_object_name = 'mailtemplate'
    template_name = "mail/mailtemplate_detail.html"
    permission_required = 'mail.read_mailtemplate'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates")),
            (reverse("mail-detail", kwargs={"pk": self.object.pk}), self.object)]
        return context


class MailCreate(PermissionRequiredMixin, CreateView):
    form_class = MailTemplateForm
    model = MailTemplate
    template_name = 'devices/base_form.html'
    permission_required = 'mail.add_mailtemplate'

    def get_initial(self):
        initial = super().get_initial()
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['type'] = "mail"
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates")),
            ("", _("Create new mailtemplate"))]
        context["formhelp"] = "mail/help.html"
        return context

    def form_valid(self, form):
        r = super().form_valid(form)
        for recipient in form.cleaned_data["default_recipients"]:
            if recipient[0] == "g":
                obj = get_object_or_404(Group, pk=recipient[1:])
            else:
                obj = get_object_or_404(Lageruser, pk=recipient[1:])
            recipient = MailTemplateRecipient(content_object=obj)
            recipient.mailtemplate = self.object
            recipient.save()
        return r


class MailUpdate(PermissionRequiredMixin, UpdateView):
    form_class = MailTemplateForm
    model = MailTemplate
    template_name = 'devices/base_form.html'
    permission_required = 'mail.change_mailtemplate'

    def get_initial(self):
        initial = super().get_initial()
        initial["default_recipients"] = [obj.content_type.name[0].lower() + str(obj.object_id) for obj in
                                         self.object.default_recipients.all()]
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates")),
            (reverse("mail-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Edit"))]
        context["formhelp"] = "mail/help.html"
        return context

    def form_valid(self, form):
        r = super().form_valid(form)
        for recipient in self.object.default_recipients.all():
            identifier = recipient.content_type.name[0].lower() + str(recipient.id)
            if identifier not in form.cleaned_data["default_recipients"]:
                recipient.delete()
            else:
                form.cleaned_data["default_recipients"].remove(identifier)
        for recipient in form.cleaned_data["default_recipients"]:
            if recipient[0] == "g":
                obj = get_object_or_404(Group, pk=recipient[1:])
            else:
                obj = get_object_or_404(Lageruser, pk=recipient[1:])
            rec = MailTemplateRecipient(content_object=obj)
            rec.mailtemplate = self.object
            rec.save()
        return r


class MailDelete(PermissionRequiredMixin, DeleteView):
    form_class = MailTemplateForm
    model = MailTemplate
    success_url = reverse_lazy('mail-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'mail.delete_mailtemplate'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates")),
            (reverse("mail-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Delete"))]
        return context
