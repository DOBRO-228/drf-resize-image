import io
import os
import random
import re
import string
from io import BytesIO
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from images.models import Image as ImageModel
from PIL import Image
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer


class DownloadImageMixin(object):
    """"""

    def download_image(self, payload_of_request):
        """
        """
        headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        }
        path_to_image = self.build_path(payload_of_request)
        if payload_of_request.get('file') is not None:
            downloaded_file = payload_of_request.get('file')
        else:
            response = requests.get(payload_of_request.get('url'), headers=headers)
            downloaded_file = BytesIO(response.content)
        image = Image.open(downloaded_file)
        image.save(path_to_image)
        return self.save_in_database(path_to_image, payload_of_request.get('url'))
    
    def save_in_database(self, path_to_image, url=None):
        opened_pil_object = Image.open(path_to_image)
        width, height = opened_pil_object.size
        name = re.search(r'([^\/]+$)', opened_pil_object.filename).group()
        image = ImageModel(
            url=url,
            name=name,
            picture=path_to_image,
            width=width,
            height=height,
            parent_picture=None,
        )
        image.save()
        print(ImageModel.objects.all())
        return image

    def build_path(self, payload_of_request):
        """"""
        cwd = os.getcwd()
        url_path = urlparse(payload_of_request.get('url')).path
        if payload_of_request.get('url') is not None:
            file_name = re.search(r'([^\/]+$)', url_path).group()
        else:
            file_name = re.sub(r'[^A-Za-z\d.-]', '_', str(payload_of_request.get('file')))
        path = '{0}/media/{1}'.format(cwd, file_name)
        if os.path.exists(path):
            file_name = self.get_uniq_filename(file_name)
        return '{0}/media/{1}'.format(cwd, file_name)

    def get_uniq_filename(self, file_name):
        random_str = ''.join(random.choices(
            string.ascii_letters + string.digits + string.ascii_uppercase + string.ascii_lowercase,
            k=7,
        ))
        dot_index = file_name.rfind('.')
        return '{0}_{1}{2}'.format(file_name[:dot_index], random_str, file_name[dot_index:])
