# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class TasksList(models.Model):

    class Meta:
        verbose_name = _("tasks list")
        verbose_name_plural = _("tasks lists")
        default_related_name = 'tasks_lists'

    name = models.CharField(verbose_name=_("name"), max_length=100,
                            unique=True)

    def __str__(self):
        return self.name
    __str__.requires_fields = ['name']


class Task(models.Model):

    class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")
        default_related_name = 'tasks'
        order_with_respect_to = 'tasks_list'
        unique_together = [('title', 'tasks_list')]

    title = models.CharField(verbose_name=_("title"), max_length=200)
    tasks_list = models.ForeignKey(
        'TasksList', models.CASCADE, verbose_name=_("tasks list"))
    description = models.TextField(
        verbose_name=_("description"), blank=True, null=True, help_text=_(
            "Please describe the task."
        ))
    is_done = models.BooleanField(verbose_name=_("done"), default=False)

    def __str__(self):
        return '[{}] {}'.format(self.taskslist, self.title)
    __str__.requires_fields = ['taskslist', 'title']
