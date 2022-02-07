import tempfile

import requests
from images.mixins import ImageHandlerMixin
from images.models import Image
from PIL import Image as PILImage
from PIL import UnidentifiedImageError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, ImageField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer


class ImageSerializer(ModelSerializer):

    class Meta:  # Noqa: WPS306
        model = Image
        fields = ['id', 'name', 'url', 'picture', 'width', 'height', 'parent_picture']


class CreateImageSerializer(ImageHandlerMixin, Serializer):

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
            raise ValidationError({'error': "You need to provide 'url' or 'file' parameter."})
        if not image_source or two_sources:
            raise ValidationError({'error': "You need to provide 'url' or 'file' parameter."})
        if image_source.get('url'):
            self.url_validation(image_source.get('url'))
            self.file_from_url_validation(image_source.get('url'))
        return image_source

    def url_validation(self, url):
        """
        Validate url.

        Args:
            url(str): Image source.

        Raises:
            ValidationError: If it's not possible to download an image from `url`.
        """
        response = requests.get(url)
        message = {
            'error': "Can't download from this url. Download request returned {0} status code.".
            format(response.status_code),
        }
        not_expected_status = 400
        if response.status_code >= not_expected_status:
            try:
                response.raise_for_status()
            except requests.exceptions.RequestException:
                raise ValidationError(message)

    def file_from_url_validation(self, url):
        """
        Validate downloaded file from url.

        Args:
            url(str): Image source.

        Raises:
            ValidationError: If downloaded file from `url` is not an image.
        """
        message = {
            'error': 'Upload a valid image. The uploaded file is not an image or is corrupted.',
        }
        with tempfile.NamedTemporaryFile() as tmp_file:
            downloaded_file = self.download_from_url(url, tmp_file)
            try:
                PILImage.open(downloaded_file)
            except UnidentifiedImageError:
                raise ValidationError(message)


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
            message = {
                'error': "You need to provide at least 'width' or 'height' parameter.",
            }
            raise ValidationError(message)
        width = size_parameters.get('width')
        height = size_parameters.get('height')
        if width:
            if width < 1:
                message = {
                    'error': "'width' and 'height' parameters must be more than 0.",
                }
                raise ValidationError(message)
        if height:
            if height < 1:
                message = {
                    'error': "'width' and 'height' parameters must be more than 0.",
                }
                raise ValidationError(message)
        return size_parameters
