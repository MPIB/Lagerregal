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

class MailList(ListView):
    model = MailTemplate
    context_object_name = 'mail_list'
    paginate_by = 30

class MailDetail(DetailView):
    model = MailTemplate
    context_object_name = 'mailtemplate'
    template_name = "mail/mailtemplate_detail.html"

class MailCreate(CreateView):
    form_class = MailTemplateForm
    model = MailTemplate
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MailCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Mailtemplate"
        context['type'] = "mail"
        return context

class MailUpdate(UpdateView):
    form_class = MailTemplateForm
    model = MailTemplate
    template_name = 'devices/base_form.html'


class MailDelete(DeleteView):
    form_class = MailTemplateForm
    model = MailTemplate
    success_url = reverse_lazy('mail-list')
    template_name = 'devices/base_delete.html'