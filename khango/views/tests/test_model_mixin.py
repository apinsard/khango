# -*- coding: utf-8 -*-
from django.db import models
from django.test import TestCase

from ..behaviors import ModelMixin


class Bar(models.Model):

    class Meta:
        app_label = 'test'

    a = models.CharField(max_length=20)
    b = models.IntegerField()
    c = models.IntegerField()


class Foo(models.Model):

    class Meta:
        app_label = 'test'

    a = models.CharField(max_length=20)
    b = models.IntegerField()
    c = models.CharField(max_length=255)
    bar = models.ForeignKey(Bar, models.CASCADE,
                            related_name='foos')


class Baz(models.Model):

    class Meta:
        app_label = 'test'

    bar = models.ForeignKey(Bar, models.CASCADE)
    foo = models.ForeignKey(Foo, models.CASCADE)

    def barbouze(self):
        return '{} {}'.format(self.bar, self.foo)
    barbouze.requires_fields = ['bar', 'foo']


class ParseFieldsTestCase(TestCase):

    def test_simplest(self):

        class FooView(ModelMixin):
            model = Foo
            fields = ['a', 'c']

        f = FooView()
        self.assertSetEqual(f.get_only(), {'a', 'c'})
        self.assertSetEqual(f.get_select_related(), set())
        self.assertSetEqual(f.get_prefetch_related(), set())

    def test_foreignkey(self):

        class FooView(ModelMixin):
            model = Foo
            fields = ['a', 'bar']

        f = FooView()
        self.assertSetEqual(f.get_only(), {'a', 'bar'})
        self.assertSetEqual(f.get_select_related(), {'bar'})
        self.assertSetEqual(f.get_prefetch_related(), set())

    def test_foreignkey_fields(self):

        class FooView(ModelMixin):
            model = Foo
            fields = ['a', 'bar__a', 'bar__b', 'b']

        f = FooView()
        self.assertSetEqual(f.get_only(), {'a', 'bar__a', 'bar__b', 'b'})
        self.assertSetEqual(f.get_select_related(), {'bar'})
        self.assertSetEqual(f.get_prefetch_related(), set())

    def test_chained_foreignkeys(self):

        class BazView(ModelMixin):
            model = Baz
            fields = ['foo__bar__a', 'foo__a', 'foo__bar__b']

        f = BazView()
        self.assertSetEqual(f.get_only(),
                            {'foo__bar__a', 'foo__a', 'foo__bar__b'})
        self.assertSetEqual(f.get_select_related(), {'foo', 'foo__bar'})
        self.assertSetEqual(f.get_prefetch_related(), set())

    def test_melted_foreignkeys(self):

        class BazView(ModelMixin):
            model = Baz
            fields = ['bar__a', 'bar__b', 'foo__bar__a', 'foo__bar__b']

        f = BazView()
        self.assertSetEqual(f.get_only(),
                            {'bar__a', 'bar__b', 'foo__bar__a', 'foo__bar__b'})
        self.assertSetEqual(f.get_select_related(), {'bar', 'foo', 'foo__bar'})
        self.assertSetEqual(f.get_prefetch_related(), set())

    def test_reverse_relation(self):

        class BarView(ModelMixin):
            model = Bar
            fields = ['a', 'foos__a', 'foos__b']

        f = BarView()
        self.assertSetEqual(f.get_only(), {'a', 'foos__a', 'foos__b'})
        self.assertSetEqual(f.get_select_related(), set())
        self.assertSetEqual(f.get_prefetch_related(), {'foos'})

    def test_many_to_many(self):
        pass

    def test_method_requires_fields(self):

        class BazView(ModelMixin):
            model = Baz
            fields = ['barbouze']

        f = BazView()
        self.assertSetEqual(f.get_only(), {'bar', 'foo'})
        self.assertSetEqual(f.get_select_related(), {'bar', 'foo'})
        self.assertSetEqual(f.get_prefetch_related(), set())
