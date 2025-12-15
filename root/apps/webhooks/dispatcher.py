from .models import WebhookSubscription
from .tasks import send_webhook_request

def emit_event(organization, event_name, data):
    webhooks = WebhookSubscription.objects.filter(
        organization=organization,
        is_active=True,
        events__contains=[event_name]
    )

    for webhook in webhooks:
        send_webhook_request.delay(
            webhook_id=webhook.id,
            url=webhook.url,
            secret=webhook.secret,
            event=event_name,
            payload=data
        )
