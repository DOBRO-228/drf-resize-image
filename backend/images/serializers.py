from images.models import Image
from rest_framework.fields import CharField, FileField, ImageField, IntegerField, URLField
from rest_framework.serializers import ModelSerializer, Serializer


class ImageSerializer(ModelSerializer):

    class Meta:
        model = Image
        fields = ['id', 'name', 'url', 'picture', 'width', 'height', 'parent_picture']


class CreateImageSerializer(Serializer):

    url = CharField(required=False)
    file = FileField(required=False)


class ResizeImageSerializer(Serializer):

    width = IntegerField(required=False)
    height = IntegerField(required=False)
