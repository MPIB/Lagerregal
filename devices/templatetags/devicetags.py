from django.template import Library, Node, TemplateSyntaxError
import re
from django.utils.safestring import mark_safe
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



class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')
@register.filter
def add_class(value, css_class):
    string = unicode(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class, 
                                                    css_class, css_class), 
                                                    match.group(1))
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class, 
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value