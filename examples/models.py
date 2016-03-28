# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class Question(models.Model):

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    title = models.CharField(
        verbose_name=_("title"),
        max_length=100,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        verbose_name=_("author"),
        related_name='questions',
        related_query_name='questions',
        blank=True,
        null=True,
    )
    content = models.TextField(
        verbose_name=_("content"),
        blank=True,
    )
    add_date = models.DateTimeField(
        verbose_name=_("published on"),
        auto_now_add=True,
    )
    update_date = models.DateTimeField(
        verbose_name=_("last updated on"),
        auto_now=True,
    )

    def __str__(self):
        return _("#{id} {title} by {author} on {date}").format(
            title=self.title,
            author=self.author,
            date=self.add_date,
        )


class Answer(models.Model):

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("answers")

    question = models.ForeignKey(
        Question, models.CASCADE,
        verbose_name=_("question"),
        related_name='answers',
        related_query_name='answers',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        verbose_name=_("author"),
        related_name='answers',
        related_query_name='answers',
        blank=True,
        null=True,
    )
    content = models.TextField(
        verbose_name=_("content"),
        blank=True,
    )
    add_date = models.DateTimeField(
        verbose_name=_("published on"),
        auto_now_add=True,
    )
    update_date = models.DateTimeField(
        verbose_name=_("last updated on"),
        auto_now=True,
    )

    def __str__(self):
        return _("#{id} answer to {title} by {author} on {date}").format(
            title=self.question.title,
            author=self.author,
            date=self.add_date,
        )
