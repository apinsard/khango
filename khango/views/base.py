# -*- coding: utf-8 -*-
from django.views.generic import (
    ListView as BaseListView,
)

from .behaviors import ModelMixin, ContentTypeMixin

__all__ = [
    'ListView',
]


class ListView(ModelMixin, ContentTypeMixin, BaseListView):
    pass
