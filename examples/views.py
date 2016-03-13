# -*- coding: utf-8 -*-
from khango.views import ListView

from .models import TasksList


class TasksListListView(ListView):

    model = TasksList
    fields = ['name']
