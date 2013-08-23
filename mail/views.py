from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View, FormView
from django.template import RequestContext, loader, Context
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy, reverse
from mail.models import MailTemplate
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.formats import localize
from django.contrib import messages
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy, reverse
from mail.forms import MailTemplateForm
from django.utils.translation import ugettext_lazy as _

class MailList(ListView):
    model = MailTemplate
    context_object_name = 'mail_list'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MailList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates"))]
        return context

    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

class MailDetail(DetailView):
    model = MailTemplate
    context_object_name = 'mailtemplate'
    template_name = "mail/mailtemplate_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MailDetail, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates")),
            (reverse("mail-detail", kwargs={"pk":self.object.pk}), self.object)]
        return context

class MailCreate(CreateView):
    form_class = MailTemplateForm
    model = MailTemplate
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MailCreate, self).get_context_data(**kwargs)
        context['type'] = "mail"
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates")),
            ("", _("Create new mailtemplate"))]
        context["formhelp"] = "mail/help.html"
        return context

class MailUpdate(UpdateView):
    form_class = MailTemplateForm
    model = MailTemplate
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MailUpdate, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates")),
            (reverse("mail-detail", kwargs={"pk":self.object.pk}), self.object),
            ("", _("Edit"))]
        context["formhelp"] = "mail/help.html"
        return context


class MailDelete(DeleteView):
    form_class = MailTemplateForm
    model = MailTemplate
    success_url = reverse_lazy('mail-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MailDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("mail-list"), _("Mailtemplates")),
            (reverse("mail-detail", kwargs={"pk":self.object.pk}), self.object),
            ("", _("Delete"))]
        return context