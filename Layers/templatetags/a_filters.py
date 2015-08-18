"""Custom filters of Kasatou."""
from django import template
register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    """Splits value to strings and return only arg joined strings."""
    line_num = int(arg)
    lst = value.split('<br>')
    if len(lst) > line_num:
        return '<br>'.join(lst[:line_num]) + "=>>"
    else:
        return '<br>'.join(lst[:line_num])
