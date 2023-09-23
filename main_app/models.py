import os
from django.db import models


def create_path(instance, name):
    return os.path.normpath(f"{instance.id}/{name}")


class File(models.Model):
    file = models.FileField(upload_to=create_path, blank=False)
    upload_at = models.DateTimeField(auto_now_add=True, blank=False)
    processed = models.BooleanField(default=False, blank=False)
