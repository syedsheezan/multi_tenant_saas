from django.urls import path
from .views import FileUploadView,FileListView

urlpatterns = [
    path("files/upload", FileUploadView.as_view()),
    path("files", FileListView.as_view()),

]
