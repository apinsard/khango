# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.test import TestCase

from ..behaviors import ContentTypeMixin


class GetContentTypeTestCase(TestCase):

    def test_not_provided(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.content_types = ['application/javascript', 'application/xml']
        self.assertEqual(f.get_content_type(), 'application/javascript')

    def test_none_matched(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = 'text/html'
        f.content_types = ['application/javascript', 'application/xml']
        self.assertIsNone(f.get_content_type())

    def test_last_matched(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = 'text/html,application/javascript'
        self.content_types = ['application/javascript', 'text/html']
        self.assertEqual(f.get_content_type(), 'text/html')

    def test_last_matched_2(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = \
            'text/html,application/javascript,application/xml+xhtml'
        f.content_types = ['application/javascript', 'text/html']
        self.assertEqual(f.get_content_type(), 'text/html')

    def test_middle_matched(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = (
            'text/html;q=0.8,application/javascript;q=0.9,'
            'application/xml+xhtml'
        )
        f.content_types = [
            'text/html', 'application/javascript', 'application/xml'
        ]
        self.assertEqual(f.get_content_type(), 'application/javascript')

    def test_none_matched_all_allowed(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = \
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        f.content_types = [
            'text/plain', 'application/javascript',
        ]
        self.assertEqual(f.get_content_type(), 'text/plain')


class GetAcceptedContentTypes(TestCase):

    def test_not_provided(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        self.assertListEqual(list(f.get_accepted_content_types()),
                             ['*/*'])

    def test_one_provided(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = 'text/html'
        self.assertListEqual(list(f.get_accepted_content_types()),
                             ['text/html'])

    def test_two_provided(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = 'text/html,application/javascript'
        self.assertListEqual(list(f.get_accepted_content_types()),
                             ['text/html', 'application/javascript'])

    def test_three_provided(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = \
            'text/html,application/javascript,application/xml+xhtml'
        self.assertListEqual(list(f.get_accepted_content_types()), [
            'text/html', 'application/javascript', 'application/xml+xhtml',
        ])

    def test_quality_provide(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = (
            'text/html;q=0.8,application/javascript;q=0.9,'
            'application/xml+xhtml'
        )
        self.assertListEqual(list(f.get_accepted_content_types()), [
            'application/xml+xhtml', 'application/javascript', 'text/html',
        ])

    def test_concrete_example(self):
        f = ContentTypeMixin()
        f.request = HttpRequest()
        f.request.META['HTTP_ACCEPT'] = \
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self.assertListEqual(list(f.get_accepted_content_types()), [
            'text/html', 'application/xhtml+xml', 'application/xml', '*/*',
        ])
