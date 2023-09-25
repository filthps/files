import os
from typing import Optional, Callable
from django.db.models.query import QuerySet
from .celery import app
from .models import File


def lock_file(f: Callable):
    def wrapper(pk, *args, path=None, **kwargs):
        if not pk:
            raise ValueError
        path = get_file_path(pk) if path is None else path
        file = open(path)
        result = f(pk, *args, file_path=path, **kwargs)
        file.close()
        return result
    return wrapper


@app.task(bind=True, reply=True)
@lock_file
def process_on_text_file(id_, file_path=None):
    if not id_:
        raise ValueError
    path = get_file_path(id_) if not file_path else file_path
    instance = get_instance_from_database(id_)
    if not instance:
        return
    with open(path, "at"):
        ...
    update_database_entry(id_, instance=instance, processed=True)


@app.task(bind=True, reply=True)
@lock_file
def process_on_image_file(id_, file_path=None):
    if not id_:
        raise ValueError
    instance = get_instance_from_database(id_)
    path = get_file_path(id_, orm_instance=instance) if not file_path else file_path
    if not instance:
        return
    with open(path, "ab"):
        ...
    update_database_entry(id_, instance=instance, processed=True)


def get_instance_from_database(pk) -> Optional[QuerySet]:
    container: QuerySet = File.objects.filter(id__exact=pk)
    if container.count():
        return container[0]


def get_file_path(pk, orm_instance=None) -> Optional[str]:
    """ Проверить актуальность записи в базе данных,
        проверить наличие в файловой системе
        :return путь к загруженному по api файлу
    """
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


def update_database_entry(pk, instance: QuerySet = None, **kw):
    if not instance:
        instance = get_instance_from_database(pk)
    if type(instance) is not QuerySet:
        raise TypeError
    instance.update(**kw)
