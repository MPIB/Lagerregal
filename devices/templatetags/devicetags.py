from django.template import Library, Node, TemplateSyntaxError


register = Library()

@register.simple_tag 
def get_verbose_name(object): 
    return object._meta.verbose_name

@register.simple_tag 
def get_verbose_name_lowercase(object): 
    return object._meta.verbose_name.lower()