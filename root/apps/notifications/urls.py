from django.urls import path
from .views import NotificationListView, NotificationMarkReadView, NotificationMarkAllReadView, NotificationCountView
urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications-list'),
    path('mark-read/', NotificationMarkReadView.as_view(), name='notifications-mark-read'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notifications-mark-all-read'),
    path('count/', NotificationCountView.as_view(), name='notifications-count'),
]
