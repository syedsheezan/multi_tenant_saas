from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.tasks.models import Task
from .models import Notification
from .tasks import send_notification_email, dispatch_push_notification

@receiver(post_save, sender=Task)
def task_post_save(sender, instance: Task, created, **kwargs):
    # fire notification when assigned_to changes or on create if assigned
    if instance.assigned_to:
        # create in-app notification
        notif = Notification.objects.create(
            organization=instance.organization,
            recipient=instance.assigned_to,
            actor=instance.created_by,
            verb="task_assigned",
            title=f"You've been assigned: {instance.title}",
            data={"task_id": str(instance.id), "project_id": str(instance.project_id), "message": f"Task assigned: {instance.title}"}
        )
        # Fire email + push asynchronously
        send_notification_email.delay(str(notif.id))
        dispatch_push_notification.delay(str(notif.id))
