# -*- coding: utf-8 -*-
from django.template import Library


register = Library()


@register.simple_tag(name='getattr')
def _getattr(*args):
    return getattr(*args)
