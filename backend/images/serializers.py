from images.models import Image
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, ImageField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer


class ImageSerializer(ModelSerializer):

    class Meta:  # Noqa: WPS306
        model = Image
        fields = ['id', 'name', 'url', 'picture', 'width', 'height', 'parent_picture']


class CreateImageSerializer(Serializer):

    url = CharField(required=False)
    file = ImageField(required=False)  # Noqa: WPS110

    def validate(self, image_source):
        """
        Validate image source.

        Args:
            image_source(dict): Image source.

        Returns:
            properties(dict): Validated image source.

        Raises:
            ValidationError: If `image_source` doesn't provide any source
                or provides more than 1 source.
        """
        two_sources = image_source.get('url') and image_source.get('file')
        if not image_source or two_sources:
            raise ValidationError("You need to provide 'url' or 'file' parameter.")
        return image_source


class ResizeImageSerializer(Serializer):

    width = IntegerField(required=False)
    height = IntegerField(required=False)

    def validate(self, size_parameters):
        """
        Validate size parameters.

        Args:
            size_parameters(dict): Size parameters.

        Returns:
            size_parameters(dict): Validated size parameters.

        Raises:
            ValidationError: If `size_parameters` doesn't provide any parameters.
            ValidationError: If `size_parameters` provides width or height less than 1.
        """
        if not size_parameters:
            raise ValidationError("You need to provide at least 'width' or 'height' parameter.")
        width = size_parameters.get('width')
        height = size_parameters.get('height')
        if width is not None:
            if width < 1:
                raise ValidationError("'width' and 'height' parameters must be more than 0.")
        if height is not None:
            if height < 1:
                raise ValidationError("'width' and 'height' parameters must be more than 0.")
        return size_parameters
