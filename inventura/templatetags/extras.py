from django import template

register = template.Library()

@register.filter
def to_unicode(mixed):
    return str(mixed)
    
@register.filter
def add_zeros(mixed):
    return "{:02d}".format(int(''.join(filter(str.isdigit, mixed))))