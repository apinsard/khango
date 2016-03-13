# -*- coding: utf-8 -*-
from django.views.generic.list import BaseListView

from .behaviors import KhangoMixin

__all__ = [
    'ListView',
]


class ListView(KhangoMixin, BaseListView):
    base_name = 'list'

    @classmethod
    def get_url_pattern(cls):
        return '^taskslist/$'

    @classmethod
    def get_url_name(cls):
        return 'taskslist_list'
