import os
import base64
import io
from typing import Optional, IO
from django.db.models.query import QuerySet
from rest_framework.views import Response
from .celery_conf import app
from .models import File


@app.task(bind=True)
def process_on_file(id_):
    path = get_file_path(id_)
    with open(path, "wb"):
        pass
    output: IO[bytes] = io.BytesIO()
    file_inner: IO = open(path, 'rb')
    base64.decode(file_inner.read(), output)


def get_instance_from_database(pk) -> Optional[QuerySet]:
    container: QuerySet = File.objects.filter(id__exact=pk)
    if container.count():
        return container[0]


def get_file_path(pk: int) -> Optional[str]:
    item = get_instance_from_database(pk)
    if not item:
        return
    file_path = item.file.path
    if not os.path.exists(os.path.abspath(file_path)):
        return
    return file_path
