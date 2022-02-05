from django.shortcuts import get_object_or_404
from images.mixins import ImageHandlerMixin
from images.models import Image
from images.serializers import CreateImageSerializer, ImageSerializer, ResizeImageSerializer
from PIL import UnidentifiedImageError
from requests.exceptions import RequestException
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class ImagesViewSet(ImageHandlerMixin, ModelViewSet):
    """Image ModelViewSet."""

    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            image = self.save_image(serializer.validated_data)
        except RequestException:
            response = {'message': "Can't download from this url. Maybe it's invalid or server doesn't respond."}  # Noqa: E501
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except UnidentifiedImageError:
            response = {'message': 'File from this url is not an image.'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        serializer = ImageSerializer(
            image, context={'request': request},
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        response = {'message': 'Method is not allowed.'}
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['POST'], detail=True, name='resize_image')
    def resize(self, request, pk=None, *args, **kwargs):
        serializer = ResizeImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parent_object = get_object_or_404(Image, pk=pk)
        resized_image = self.resize_image(request.data, parent_object)
        serializer = ImageSerializer(resized_image, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
