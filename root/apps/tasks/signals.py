# apps/tasks/signals.py
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver

from .models import Task, TaskComment
from apps.webhooks.dispatcher import emit_event

def build_task_payload(task: Task) -> dict:
    """Return a serializable representation of the task for webhook payloads."""
    return {
        "task_id": task.id,
        "project_id": getattr(task.project, "id", None),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": getattr(task, "priority", None),
        "assigned_to": getattr(task.assigned_to, "id", None),
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "updated_at": task.updated_at.isoformat() if getattr(task, "updated_at", None) else None,
    }

def build_comment_payload(comment: TaskComment) -> dict:
    """Return a serializable representation of a comment for webhook payloads."""
    return {
        "comment_id": comment.id,
        "task_id": getattr(comment.task, "id", None),
        "user_id": getattr(comment.user, "id", None),
        "comment": comment.comment,
        "created_at": comment.created_at.isoformat() if getattr(comment, "created_at", None) else None,
    }

@receiver(post_save, sender=Task)
def task_post_save(sender, instance: Task, created: bool, **kwargs):
    """
    Fires:
      - 'task.created' when created == True
      - 'task.updated' for updates (created == False)
    NOTE: uses transaction.on_commit to ensure webhook jobs only enqueue after commit.
    """
    event = "task.created" if created else "task.updated"
    payload = build_task_payload(instance)

    # Use transaction.on_commit to avoid firing webhooks on failed transactions.
    transaction.on_commit(lambda: emit_event(instance.project.organization, event, payload))

@receiver(post_save, sender=TaskComment)
def comment_post_save(sender, instance: TaskComment, created: bool, **kwargs):
    """
    Fires 'comment.added' when a TaskComment is created.
    If you want an event on comment update, add logic similar to Task above.
    """
    if not created:
        return

    payload = build_comment_payload(instance)
    transaction.on_commit(lambda: emit_event(instance.task.project.organization, "comment.added", payload))
