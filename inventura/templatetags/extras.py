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
def revije_nav(tip, root, selected):
    object_list = Tiskovina.objects.all()
    if not selected:
        selected = object_list
    return {'revije': object_list, 'selected': tip, 'root': root, 'object_list': selected }