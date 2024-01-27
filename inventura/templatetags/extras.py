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
    object_list = Tiskovina.objects.all().order_by('eksponat')
    if not selected:
        selected = object_list
    return {'vserevije': object_list, 'selected': tip, 'root': root, 'object_list': selected }

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)

@register.filter()
def groups_sort(groups):
    groups.sort(key=lambda group: len(group[1]))
    return groups

@register.filter()
def groups_sort_reversed(groups):
    groups.sort(key=lambda group: len(group[1]), reverse=True)
    return groups

@register.filter()
def get_cover(tiskovina):
    return tiskovina.naslovnica