import os
import tempfile
from urllib.parse import urlparse

import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from images.models import Image
from PIL import Image as PILImage


class ImageHandlerMixin(object):
    """Mixin provides save and resize image methods."""

    def save_image(self, request_payload):
        """
        Download image from url or save provided image.

        Args:
            request_payload(dict): Request payload - url or file.

        Returns:
            image_object(models.Image): New instance of Image object.
        """
        with tempfile.NamedTemporaryFile() as tmp_file:
            if request_payload.get('file') is not None:
                downloaded_file = request_payload.get('file')
            else:
                downloaded_file = self.download_from_url(request_payload.get('url'), tmp_file)
            with PILImage.open(downloaded_file) as image:
                width, height = image.size
                image.save(tmp_file, image.format)
            tmp_file.name = downloaded_file.name
            return self.create_new_image_instance(
                tmp_file,
                width=width,
                height=height,
                url=request_payload.get('url'),
            )

    def download_from_url(self, url, temporary_file):
        """
        Download image from url.

        Args:
            temporary_file(file): Temporary file, where to write a downloaded image.

        Returns:
            temporary_file(file): Temporary file containing an image.
        """
        with requests.get(url, stream=True) as downloaded_file:
            downloaded_file.raise_for_status()
            for chunk in downloaded_file.iter_content(chunk_size=8192):  # Noqa: WPS432
                temporary_file.write(chunk)
        path = urlparse(url).path
        filename = path.split('/').pop()
        temporary_file.name = filename
        return temporary_file

    def resize_image(self, request_payload, parent_object):
        """
        Resize image.

        Args:
            request_payload(dict): New width and height of image.
            parent_object(models.Image): Parent Image which need to resize.

        Returns:
            image_object(models.Image): New instance of Image object.
        """
        with tempfile.NamedTemporaryFile() as tmp_file:
            with PILImage.open(parent_object.picture.file) as image:
                properties = self.define_new_properties(
                    image, request_payload, parent_object.picture.name,
                )
                resized_image = image.resize(
                    (properties.get('width'), properties.get('height')),
                )
                resized_image.save(tmp_file, image.format)
            tmp_file.name = properties.get('name')
            return self.create_new_image_instance(
                tmp_file,
                width=properties.get('width'),
                height=properties.get('height'),
                parent_object=parent_object,
            )

    def define_new_properties(self, pillow_object, request_payload, parent_name):
        """
        Define new properties for image which need to resize.

        Args:
            pillow_object(object): Opened image via Pillow.
            request_payload(dict): New width and height of image.
            parent_name(str): Parent Image which need to resize.

        Returns:
            properties(dict): Properties for image which need to resize.
        """
        name, ext = os.path.splitext(parent_name)
        if request_payload.get('width') is not None:
            width = request_payload.get('width')
            name = '{0}_{1}'.format(name, width)
        else:
            width = pillow_object.width
            name = '{0}_0'.format(name)
        if request_payload.get('height') is not None:
            height = request_payload.get('height')
            name = '{0}_{1}'.format(name, height)
        else:
            height = pillow_object.height
            name = '{0}_0'.format(name)
        return {
            'width': int(width),
            'height': int(height),
            'name': '{0}{1}'.format(name, ext),
        }

    def create_new_image_instance(self, temporary_file, **kwargs):
        """
        Create new image instance.

        Args:
            temporary_file(file): Temporary file containing an image.

        Returns:
            properties(dict): Properties for image which need to resize.
        """
        image_file = InMemoryUploadedFile(
            temporary_file,
            None,
            temporary_file.name,
            'image/jpeg',
            None,
            None,
        )
        if kwargs.get('parent_object'):
            url = kwargs.get('parent_object').url
        else:
            url = kwargs.get('url')
        image = Image(
            url=url,
            picture=image_file,
            width=kwargs.get('width'),
            height=kwargs.get('height'),
            parent_picture=kwargs.get('parent_object'),
        )
        image.save()
        return image
