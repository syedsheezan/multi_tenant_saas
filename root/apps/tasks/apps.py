# apps/tasks/apps.py
from django.apps import AppConfig

class TasksConfig(AppConfig):
    name = "apps.tasks"
    verbose_name = "Tasks"

    def ready(self):
        # import signals so they are registered
        from . import signals  # noqa: F401
