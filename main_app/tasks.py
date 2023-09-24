import os
import base64
import io
from typing import Optional, IO, Callable
from django.db.models.query import QuerySet
from rest_framework.views import Response
from .celery_conf import app
from .models import File


def lock_file(f: Callable):
    def wrapper(pk, *args, **kwargs):
        if not pk:
            raise ValueError
        path = get_file_path(pk)
        file = open(path)
        result = f(pk, *args, file_path=path, **kwargs)
        file.close()
        return result
    return wrapper


@app.task(bind=True)
@lock_file
def process_on_file(id_, file_path=None):
    if not id_:
        raise ValueError
    path = get_file_path(id_) if not file_path else file_path
    with open(path, "wb"):
        pass
    #output: IO[bytes] = io.BytesIO()
    #file_inner: IO = open(path, 'rb')
    #base64.decode(file_inner.read(), output)
    instance = get_instance_from_database(id_)
    if not instance.exists():
        return


def get_instance_from_database(pk) -> Optional[QuerySet]:
    container: QuerySet = File.objects.filter(id__exact=pk)
    if container.count():
        return container[0]


def get_file_path(pk, orm_instance=None) -> Optional[str]:
    if orm_instance:
        if type(orm_instance) is not QuerySet:
            raise TypeError
        item = orm_instance
    else:
        item = get_instance_from_database(pk)
    if not item:
        return
    file_path = item.file.path
    if not os.path.exists(os.path.abspath(file_path)):
        return
    return file_path
