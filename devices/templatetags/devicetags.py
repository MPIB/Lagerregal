import os
import re
import urllib

from django.forms import CheckboxInput
from django.template import Library
from django.urls import reverse
from django.utils.html import format_html
from django.utils.html import mark_safe

from devices.models import Bookmark

register = Library()


@register.simple_tag
def get_verbose_name(object):
    return object._meta.verbose_name


@register.simple_tag
def history_compare(old, new):
    if old != new:
        if old == "" and new != "":
            return format_html("+ <span class='diff add'>{0}</span>", new)
        elif old != "" and new == "":
            return format_html("- <span class='diff remove'>{0}</span>", new)
        else:
            return format_html("<span class='diff'>{0}</span>", new)
    else:
        return new


@register.filter("is_select")
def is_select(form_field_obj):
    return (form_field_obj.field.widget.__class__.__name__ == "Select2Widget")


@register.filter("is_selectmultiple")
def is_selectmultiple(form_field_obj):
    return (form_field_obj.field.widget.__class__.__name__ == "Select2MultipleWidget")


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')


@register.filter
def add_class(value, css_class):
    string = str(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class,
                                                    css_class, css_class),
                      match.group(1))

        if m is not None:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class,
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value


@register.filter
def get_range(value):
    return list(range(value))


@register.filter
def check_bookmark(device, user):
    return Bookmark.objects.filter(user=user.id, device=device.id).exists()


@register.filter
def get_attribute(object, attribute):
    try:
        return getattr(object, attribute)
    except AttributeError:
        return object.get(attribute)


@register.filter
def filename(value):
    return os.path.basename(value.file.name)


@register.simple_tag
def as_nested_list(factvalue):
    res = ''
    if isinstance(factvalue, dict):
        res += "<ul>"
        for key, value in factvalue.items():
            if isinstance(value, dict):
                res += "<li>{}<ul>".format(key)
                for key, value in value.items():
                    res += "<li>{} : {}</li>".format(key, value)
                res += "</ul></li>"
            else:
                res += "<li>{} : {}</li>".format(key, value)
        res += "</ul>"
    elif isinstance(factvalue, list):
        res += "<ul>"
        for item in factvalue:
            res += "<li>{}</li>".format(item)
        res += "</ul>"
    else:
        res += str(factvalue)

    return mark_safe(res)


@register.filter
def splitstr(arg1, arg2):
    return arg1.split(arg2)


@register.inclusion_tag('snippets/deletebutton.html')
def deletebutton(viewname, *args):
    return {
        'url': reverse(viewname, args=args)
    }


@register.simple_tag(takes_context=True)
def current_url(context, **kwargs):
    path = context['request'].get_full_path()
    if '?' in path:
        path, qs = path.split('?', 1)
        query = urllib.parse.parse_qs(qs)
    else:
        query = {}
    query.update(kwargs)
    qs = urllib.parse.urlencode(query, doseq=True)
    return path + '?' + qs
