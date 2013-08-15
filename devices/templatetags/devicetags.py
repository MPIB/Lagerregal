from django.template import Library, Node, TemplateSyntaxError


register = Library()

@register.simple_tag 
def get_verbose_name(object): 
    return object._meta.verbose_name

@register.simple_tag 
def get_verbose_name_lowercase(object): 
    return object._meta.verbose_name.lower()

@register.simple_tag
def history_compare(old, new):
    print old, new
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