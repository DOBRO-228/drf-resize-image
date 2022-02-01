
import os

from config.settings import MEDIA_ROOT
from images.mixins import DownloadImageMixin
from images.models import Image
from images.serializers import CreateImageSerializer, ImageSerializer, ResizeImageSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class ImageListView(ReadOnlyModelViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class ImagesViewSet(DownloadImageMixin, ModelViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        print(type(request.data))
        serializer = CreateImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        both_parameters = serializer.data.get('url') and serializer.data.get('file')
        if not serializer.data or both_parameters:
            response = {'message': "You need to provide only 'url' or only 'file' parameter."}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if request.FILES:
            image = self.download_image(request.FILES)
        else:
            image = self.download_image(serializer.data)
        serializer = ImageSerializer(image, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print('{0}/{1}'.format(MEDIA_ROOT, instance.name))
        os.remove('{0}/{1}'.format(MEDIA_ROOT, instance.name))
        return super().destroy(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        if kwargs.pop('resize', False):
            return super().update(request, *args, **kwargs)
        response = {'message': 'Method is forbidden.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['POST'], name='Resize image')
    def resize(self, request, pk=None, *args, **kwargs):
        """"""
        self.serializer_class = ResizeImageSerializer
        kwargs['resize'] = True
        return self.partial_update(request, *args, **kwargs)
