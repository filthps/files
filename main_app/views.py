from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import ListAPIView
from .models import File
from .serializers import FileSerializer
from .tasks import process_on_text_file, process_on_image_file

MAX_SIZE = 2 * 1024 * 1024


class UploadFile(APIView):
    @staticmethod
    def post(req):
        file: InMemoryUploadedFile = req.FILES.get("file", None)
        if file.size > MAX_SIZE:
            return Response(status=413)
        file_string = str(b"".join(file.chunks()))
        serialized = FileSerializer(data={"file": file, "type": file.content_type, "body": file_string})
        if not serialized.is_valid():
            print(serialized.errors)
            return Response(status=204)
        serialized.save()
        type_ = serialized.validated_data["type"].split("/")[0]
        if type_ == "image":
            process_on_image_file.apply_async(id_=serialized.data["id"])
        if type_ == "text":
            process_on_text_file.apply_async(id_=serialized.data["id"])
        return Response(file_string, status=201)


class FileStatus(ListAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    renderer_classes = (JSONRenderer,)
