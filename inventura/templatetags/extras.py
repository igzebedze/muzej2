from django import template
from inventura.models import Tiskovina

register = template.Library()

@register.filter
def to_unicode(mixed):
    return str(mixed)
    
@register.filter
def add_zeros(mixed):
    return "{:02d}".format(int(''.join(filter(str.isdigit, mixed))))

@register.inclusion_tag('inventura/revije_nav_tag.html')
def revije_nav(tip, root):
    object_list = Tiskovina.objects.all()
    return {'object_list': object_list, 'selected': tip, 'root': root }