# apps/webhooks/urls.py
from django.urls import path
from .views import WebhookListCreateAPIView, WebhookDetailAPIView

urlpatterns = [
    path("webhooks/", WebhookListCreateAPIView.as_view(), name="webhook-list-create"),
    path("webhooks/<int:pk>/", WebhookDetailAPIView.as_view(), name="webhook-detail"),
]
