import re

from django.template import Library
from django.utils.safestring import mark_safe
from django.forms import CheckboxInput

register = Library()


@register.simple_tag
def get_verbose_name(object):
    return object._meta.verbose_name


@register.simple_tag
def get_verbose_name_lowercase(object):
    return object._meta.verbose_name.lower()


@register.simple_tag
def history_compare(old, new):
    if old != new:
        if old == "" and new != "":
            return "+ <span class='diff add'>{0}</span>".format(new)
        elif old != "" and new == "":
            return "<span class='diff remove'>-</span>".format(new)
        else:
            return "<span class='diff'>{0}</span>".format(new)
    else:
        return new


@register.filter("is_select")
def is_select(form_field_obj):
    return (form_field_obj.field.widget.__class__.__name__ == "Select")


@register.filter("is_selectmultiple")
def is_selectmultiple(form_field_obj):
    return (form_field_obj.field.widget.__class__.__name__ == "SelectMultiple")


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')


@register.filter
def add_class(value, css_class):
    string = unicode(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class,
                                                    css_class, css_class),
                      match.group(1))

        if m != None:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class,
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value


@register.filter
def get_range(value):
    return range(value)


@register.filter
def check_bookmark(device, user):
    return device.bookmarkers.filter(id=user.id).exists()


@register.filter
def get_attribute(device, attribute):
    return getattr(device, attribute)


@register.filter
def get_attribute_from_list(device, attribute):
    return device[attribute]
