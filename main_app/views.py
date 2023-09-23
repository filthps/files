from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import ListAPIView
from .models import File
from .serializers import FileSerializer
from .tasks import process_on_file


class UploadFile(APIView):
    def post(self, req, **kw):
        serialized = FileSerializer(data=req.POST)
        if not serialized.is_valid():
            return Response(status=204)
        serialized.save()
        process_on_file.apply_async(args=[serialized.fields.id])
        print(serialized.fields.id)
        Response(status=200)


class FileStatus(ListAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    renderer_classes = (JSONRenderer,)

