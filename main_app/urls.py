from django.urls import path
from main_app.views import UploadFile, FileStatus


urlpatterns = [
    path('upload/', UploadFile.as_view(), name="upload"),
    path('files/', FileStatus.as_view())
]
