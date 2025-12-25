from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.tasks.models import Task
from apps.project.models import Project
from apps.tenants.models import Invitation
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

# ----------------------------
# Project Assigned Notification
# ----------------------------
@receiver(post_save, sender=Project)
def project_assignment_post_save(sender, instance: Project, created, **kwargs):
    if instance.assigned_to:
        notif = Notification.objects.create(
            organization=instance.organization,
            recipient=instance.assigned_to,
            actor=instance.created_by,
            verb="project_assigned",
            title=f"You have been assigned to Project: {instance.name}",
            data={"project_id": str(instance.id), "project_name": instance.name}
        )
        send_notification_email.delay(str(notif.id))
        dispatch_push_notification.delay(str(notif.id))


@receiver(post_save, sender=Invitation)
def invitation_post_save(sender, instance, created, **kwargs):
    if created:
        # Notification for invited user (if they have an account)
        # If invited user doesn't exist yet, we can skip recipient or assign later
        # For now we send notification to invited_by (owner) that invite was sent
        notif = Notification.objects.create(
            organization=instance.organization,
            recipient=instance.invited_user,  # owner/admin who invited
            actor=instance.invited_by,
            verb="member_invited",
            title=f"You invited {instance.email} to join {instance.organization.name}",
            data={"email": instance.email, "organization_id": str(instance.organization.id)}
        )
        # Fire email (if invited user already has an account email, optional)
        send_notification_email.delay(str(notif.id))
        dispatch_push_notification.delay(str(notif.id))