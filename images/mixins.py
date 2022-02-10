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
            if request_payload.get('file'):
                image_to_save = request_payload.get('file')
            else:
                tmp_file = self.download_from_url(request_payload.get('url'), tmp_file)
                image_to_save = tmp_file
            return self.create_new_image_instance(
                image_to_save,
                url=request_payload.get('url'),
            )

    def download_from_url(self, url, tmp_file):
        """
        Download image from `url` and write it into `tmp_file`.

        Args:
            tmp_file(file): Temporary file, where to write a downloaded image.

        Returns:
            tmp_file(file): Temporary file containing an image.
        """
        with requests.get(url, stream=True) as downloaded_file:
            for chunk in downloaded_file.iter_content(chunk_size=8192):  # Noqa: WPS432
                tmp_file.write(chunk)
        path = urlparse(url).path
        tmp_file.name = path.split('/').pop()
        return tmp_file

    def resize_image(self, request_payload, parent_object):
        """
        Resize image.

        Args:
            request_payload(dict): New width and height of image.
            parent_object(models.Image): Parent Image which need to resize.

        Returns:
            image_object(models.Image): New instance of Image object.
        """
        if request_payload.get('width'):
            width = request_payload.get('width')
        else:
            width = parent_object.width
        if request_payload.get('height'):
            height = request_payload.get('height')
        else:
            height = parent_object.height
        with tempfile.NamedTemporaryFile() as tmp_file:
            with PILImage.open(parent_object.picture.file) as image:
                resized_image = image.resize((int(width), int(height)))
                resized_image.save(tmp_file, image.format)
            tmp_file.name = self.define_new_name(request_payload, parent_object.picture.name)
            return self.create_new_image_instance(
                tmp_file,
                parent_object=parent_object,
            )

    def define_new_name(self, request_payload, parent_name):
        """
        Define new properties for image which need to resize.

        Args:
            request_payload(dict): New width and height of image.
            parent_name(str): Parent Image which need to resize.

        Returns:
            resized_image_name(str): Name of resized image.
        """
        name, ext = os.path.splitext(parent_name)
        if request_payload.get('width'):
            name = '{0}_{1}'.format(name, request_payload.get('width'))
        else:
            name = '{0}_0'.format(name)
        if request_payload.get('height'):
            name = '{0}_{1}'.format(name, request_payload.get('height'))
        else:
            name = '{0}_0'.format(name)
        return '{0}{1}'.format(name, ext)

    def create_new_image_instance(self, temporary_file, **kwargs):
        """
        Create new image instance.

        Args:
            temporary_file(file): Temporary file containing an image.

        Returns:
            image_object(models.Image): New instance of Image object.
        """
        parent_picture = kwargs.get('parent_object')
        image_file = InMemoryUploadedFile(
            temporary_file,
            None,
            temporary_file.name,
            'image/jpeg',
            None,
            None,
        )
        if parent_picture:
            url = parent_picture.url
        else:
            url = kwargs.get('url')
        image = Image(url=url, picture=image_file, parent_picture=parent_picture)
        image.save()
        return image
