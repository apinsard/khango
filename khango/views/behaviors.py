# -*- coding: utf-8 -*-
import logging
import re

from django.core.exceptions import FieldDoesNotExist
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger('django.request')


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


class ContentTypeMixin:
    """Return a suitable response according to the "Accept" request header."""

    content_types = [
        'text/html', 'application/json', 'application/xml',
    ]

    def dispatch(self, request, *args, **kwargs):
        """Check if we can answer the request with an acceptable content-type.
        If not, return HTTP 406 "Not Acceptable".
        """
        self.content_type = self.get_content_type()
        if self.content_type is None:
            return self.http_not_acceptable(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        """Select the response method according to the requested content type.
        May raise NotImplementedError if no method matched.
        """
        response_kwargs['content_type'] = self.content_type
        if self.content_type == 'text/html':
            return self.render_html(context, **response_kwargs)
        elif self.content_type == 'application/json':
            return self.render_json(context, **response_kwargs)
        elif self.content_type == 'application/xml':
            return self.render_xml(context, **response_kwargs)
        else:
            raise NotImplementedError(
                ("Render method for content type "
                 "\"{}\" does not exist.").format(self.content_type)
            )

    def render_html(self, context, **response_kwargs):
        """Return an HTML response."""
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )

    def render_json(self, context, **response_kwargs):
        """Return context as JSON response."""
        data = context.flatten()
        del data['False'], data['True'], data['None']
        return JsonResponse(data, **response_kwargs)

    def render_xml(self, context, **response_kwargs):
        """Return an XML response."""
        raise NotImplementedError

    def http_not_acceptable(self, request, *args, **kwargs):
        logger.warning("Not Acceptable (%s): %s",
                       request.META.get('HTTP_ACCEPT'), request.path,
                       extra={
                           'status_code': 406,
                           'request': request,
                       })
        header = 'Accept'
        values = ','.join(self.get_available_content_types())
        return HttpResponse('{}: {}'.format(header, values), status_code=406,
                            content_type='text/plain')

    def get_content_type(self):
        """Return the first content type accepted by the client and that we
        know how to respond as well.
        Return None if we are not able to respond with an acceptable content
        type.
        """
        content_types = self.content_types
        accepted = list(self.get_accepted_content_types())
        for content_type in accepted:
            if content_type in content_types:
                return content_type
        if '*/*' in accepted:
            return content_types[0]
        return None

    def get_accepted_content_types(self):
        """Return the list of content types accepted by the client for the
        current request.
        """
        def qualify(x):
            parts = x.split(';', 1)
            if len(parts) == 2:
                match = re.match(r'(^|;)q=(0(\.\d{,3})?|1(\.0{,3})?)(;|$)',
                                 parts[1])
                if match:
                    return parts[0], float(match.group(2))
            return parts[0], 1

        http_accept = self.request.META.get('HTTP_ACCEPT', '*/*')
        raw_content_types = http_accept.split(',')
        qualified_content_types = map(qualify, raw_content_types)
        return (x[0] for x in sorted(qualified_content_types,
                                     key=lambda x: x[1], reverse=True))
