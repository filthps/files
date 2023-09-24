import base64
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import ListAPIView
from .models import File
from .serializers import FileSerializer
from .tasks import process_on_file


def serialize_file(file: InMemoryUploadedFile):
    return file.open("rb").read()


class UploadFile(APIView):
    def post(self, req, **kw):
        serialized = FileSerializer(data={"file": req.FILES["file"]})
        if not serialized.is_valid():
            return Response(status=204)
        serialized.save()
        file_inner = serialize_file(req.FILES["file"])
        process_on_file.apply_async(id_=serialized.data["id"])
        return Response(file_inner, status=201)


class FileStatus(ListAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    renderer_classes = (JSONRenderer,)
