# -*- coding: utf-8 -*-
from django.core.exceptions import FieldDoesNotExist


class ModelMixin:
    """Select all and only requested fields.
    Guess all required joins.
    """

    model = None
    """The model to lookup."""

    fields = None
    """List of fields we want to use.
    A field is either:
        - an actual model field
        - a reverse related field
        - a model method
    """

    __fields = None
    __only = None
    __select_related = None
    __prefetch_related = None

    def get_base_queryset(self):
        """Return the base queryset from which `get_queryset()` will start."""
        return self.model._default_manager.all()

    def get_queryset(self):
        """Select only requested fields and do accurate joins."""
        queryset = self.get_base_queryset()

        only = self.get_only()
        if only:
            queryset = queryset.only(*only)

        select_related = self.get_select_related()
        if select_related:
            queryset = queryset.select_related(*select_related)

        prefetch_related = self.get_prefetch_related()
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        return queryset

    @classmethod
    def _parse_fields(cls):
        """Iterate cls.fields and parse them to guess fields and related."""
        if cls.fields is None:
            raise ValueError((
                "You must set {}.fields, or using ModelMixin is useless."
            ).format(cls))
        if cls.__fields is not None:
            return  # Job is already done.
        cls.__fields = {}
        cls.__only = set()
        cls.__select_related = set()
        cls.__prefetch_related = set()
        for field_name in cls.fields:
            field = cls._parse_field(field_name, cls.model)
            cls.__fields[field_name] = field

    @classmethod
    def _parse_field(cls, field_name, model, base_name=''):
        field_name_parts = field_name.split('__', 1)
        try:
            field = model._meta.get_field(field_name_parts[0])
        except FieldDoesNotExist as e:
            if hasattr(model, field_name_parts[0]):
                attr = getattr(model, field_name_parts[0])
                if hasattr(attr, 'rel'):
                    field = attr.rel
                else:
                    if hasattr(attr, 'requires_fields'):
                        for f in getattr(attr, 'requires_fields'):
                            cls._parse_field(f, model, base_name)
                    return attr
            else:
                raise e
        if base_name:
            base_name = '{}__{}'.format(base_name, field_name_parts[0])
        else:
            base_name = field_name_parts[0]
        if field.many_to_one or field.one_to_one:
            cls.__select_related.add(base_name)
        elif field.many_to_many or field.one_to_many:
            cls.__prefetch_related.add(base_name)
        if len(field_name_parts) == 1:
            cls.__only.add(base_name)
            return field
        else:
            return cls._parse_field(field_name_parts[1], field.related_model,
                                    base_name)

    @classmethod
    def get_fields(cls):
        cls._parse_fields()
        return cls.__fields

    @classmethod
    def get_field(cls, name):
        cls._parse_fields()
        return cls.__fields[name]

    @classmethod
    def get_only(cls):
        cls._parse_fields()
        return cls.__only

    @classmethod
    def get_select_related(cls):
        cls._parse_fields()
        return cls.__select_related

    @classmethod
    def get_prefetch_related(cls):
        cls._parse_fields()
        return cls.__prefetch_related
