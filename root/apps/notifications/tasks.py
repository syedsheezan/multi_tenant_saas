from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Notification
from django.template.loader import render_to_string
from django.utils import timezone

@shared_task(bind=True)
def send_notification_email(self, notification_id):
    """
    Fetch Notification by id and send email to recipient if email present.
    Retries on exception.
    """
    try:
        notif = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"

    recipient_email = notif.recipient.email
    if not recipient_email:
        return "No recipient email"

    subject = notif.title or f"Notification: {notif.verb}"
    # simple message; you can render an HTML template
    message = notif.data.get("message") if notif.data and isinstance(notif.data, dict) else ""
    if not message:
        # fallback message
        message = f"You have a new notification: {notif.verb}"

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        notif.sent_via_email = True
        notif.save(update_fields=["sent_via_email"])
        return f"Email sent to {recipient_email}"
    except Exception as exc:
        # retry with exponential backoff
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task
def dispatch_push_notification(notification_id):
    """
    Placeholder for push / websocket / fcm sending.
    Implement channels or push provider here.
    """
    try:
        notif = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return "Not found"
    # For now just return payload; integration later
    payload = {
        "id": str(notif.id),
        "verb": notif.verb,
        "title": notif.title,
        "data": notif.data,
        "recipient": notif.recipient.id
    }
    # TODO: integrate channels / fcm
    return payload
