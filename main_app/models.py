import os
import re
import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.db import models


def create_path(instance, name):
    return os.path.normpath(f"{instance.id}/{name}")


def is_valid_mime_type(string: str):
    if not re.match(r"(?!image\/plain)((image|text)\/(jpg|jpeg|png|gif|plain))", string).group():
        raise ValidationError("Данный mime-type не поддерживается")


def is_image_broken(file: InMemoryUploadedFile):
    if not file.content_type.split("/")[0] == "image":
        return
    b = b"".join(file.chunks())
    try:
        image = Image.open(io.BytesIO(b))
    except Exception as details:  # Не нашёл нужного исключения
        print(details)
        raise ValidationError("Загружаемое изображение повреждено")
    image.close()


class File(models.Model):
    file = models.FileField(upload_to=create_path, blank=False, validators=[is_image_broken])
    upload_at = models.DateTimeField(auto_now_add=True, blank=False)
    processed = models.BooleanField(default=False, blank=False)
    type = models.CharField(max_length=25, blank=False, validators=[is_valid_mime_type])
    body = models.BinaryField(default=b"", blank=False)

    def save(self, *args, **kwargs):
        self.body = bytes(self.body, "utf-8") if self.body else b""
        super().save(*args, **kwargs)
