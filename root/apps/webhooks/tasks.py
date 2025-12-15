from celery import shared_task
import hashlib, hmac, requests, json

@shared_task(bind=True, max_retries=5)
def send_webhook_request(self, webhook_id, url, secret, event, payload):
    try:
        body = json.dumps({"event": event, "payload": payload})

        signature = hmac.new(
            secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
        }

        response = requests.post(url, data=body, headers=headers, timeout=5)

        if response.status_code >= 400:
            raise Exception(f"Webhook failed: {response.status_code}")

    except Exception as exc:
        retry_in = 2 ** self.request.retries
        raise self.retry(exc=exc, countdown=retry_in)
