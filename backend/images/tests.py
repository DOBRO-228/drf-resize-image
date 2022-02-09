import json
import os
import shutil
import tempfile
from random import choice

import factory
import requests
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from images.factories import ImageFactory
from images.mixins import ImageHandlerMixin
from images.models import Image
from mock import patch
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APITestCase


class ImagesTest(APITestCase):
    """Test ModelViewSet."""

    def setUp(self):
        """Prepare data for tests."""
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        factory.create_batch(ImageFactory, 3)
        self.image = ImageFactory.create()
        self.download_from_url = 'https://i.ibb.co/sJHms9y/ricardo.jpg'

    @classmethod
    def tearDownClass(cls):
        """Destroy directory in which files will upload during testing."""
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_get_list(self):
        """Test getting list of objects."""
        response = self.client.get(reverse('images-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(Image.objects.all()))

    def test_get_detail_image(self):
        """Test getting detail object information."""
        url = reverse('images-detail', kwargs={'pk': self.image.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)
        self.assertEqual(response.data['id'], self.image.id)
        self.assertEqual(response.data['name'], self.image.name)
        self.assertEqual(response.data['url'], self.image.url)
        self.assertEqual(response.data['width'], self.image.width)
        self.assertEqual(response.data['height'], self.image.height)
        self.assertEqual(response.data['parent_picture'], self.image.parent_picture)

    def test_destroy(self):
        """Test destroying object."""
        created_image = ImageFactory()
        url_get = reverse('images-detail', kwargs={'pk': created_image.id})
        response = self.client.get(url_get)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url_delete = reverse('images-detail', kwargs={'pk': created_image.id})
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Image.DoesNotExist):
            Image.objects.get(pk=created_image.id)
        response = self.client.get(url_get)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_from_url(self):
        """Test creating object from url."""
        request_payload = {'url': self.download_from_url}
        response = self.client.post(
            reverse('images-list'),
            data=json.dumps(request_payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        image_qs = Image.objects.filter(pk=response.data['id'])
        self.assertTrue(image_qs.exists())
        image_instance = Image.objects.get(pk=response.data['id'])
        self.assertEqual(response.data['url'], image_instance.url)
        self.assertEqual(self.download_from_url, image_instance.url)

    def test_create_from_file(self):
        """Test creating object from file."""
        request_payload = {'file': self.image.picture.file}
        response = self.client.post(
            reverse('images-list'),
            data=request_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        image_qs = Image.objects.filter(pk=response.data['id'])
        self.assertTrue(image_qs.exists())
        image_instance = Image.objects.get(pk=response.data['id'])
        self.assertNotEqual(self.image.picture.file, image_instance.picture.file)

    def test_resize_width_and_height(self):  # Noqa: WPS210
        """Test resizing width and height."""
        new_widths = set(range(1, 500))
        new_heights = set(range(1, 500))
        new_widths.discard(self.image.width)
        new_heights.discard(self.image.height)
        new_width = choice(list(new_widths))
        new_height = choice(list(new_heights))
        url = reverse('images-resize', kwargs={'pk': self.image.id})
        request_payload = {'width': new_width, 'height': new_height}
        response = self.client.post(
            url,
            data=json.dumps(request_payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        resized_image = Image.objects.get(pk=response.data['id'])
        with PILImage.open(resized_image.picture.file) as image:
            self.assertEqual(image.size, (new_width, new_height))
        self.assertEqual(resized_image.parent_picture, self.image)
        self.assertTrue(str(new_width) and str(new_height) in resized_image.name)

    def test_resize_width_only(self):  # Noqa: WPS210
        """Test resizing width only."""
        new_widths = set(range(1, 500))
        new_widths.discard(self.image.width)
        new_width = choice(list(new_widths))
        url = reverse('images-resize', kwargs={'pk': self.image.id})
        request_payload_with_width = {'width': new_width}
        response = self.client.post(
            url,
            data=json.dumps(request_payload_with_width),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        resized_image = Image.objects.get(pk=response.data['id'])
        with PILImage.open(resized_image.picture.file) as image:
            self.assertEqual(image.width, new_width)
        self.assertTrue(str(new_width) and '_0.' in resized_image.name)

    def test_resize_height_only(self):  # Noqa: WPS210
        """Test resizing height only."""
        new_heights = set(range(1, 500))
        new_heights.discard(self.image.height)
        new_height = choice(list(new_heights))
        url = reverse('images-resize', kwargs={'pk': self.image.id})
        request_payload_with_width = {'height': new_height}
        response = self.client.post(
            url,
            data=json.dumps(request_payload_with_width),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        resized_image = Image.objects.get(pk=response.data['id'])
        with PILImage.open(resized_image.picture.file) as image:
            self.assertEqual(image.height, new_height)
        self.assertTrue('_0_' and str(new_height) in resized_image.name)


class ValidationTest(APITestCase):
    """Test validation."""

    def setUp(self):
        """Prepare data for tests."""
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        self.image = ImageFactory.create()

    @classmethod
    def tearDownClass(cls):
        """Destroy directory in which files will upload during testing."""
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_parameters_validation(self):
        """Test create method parameters validation."""
        request_payload = {}
        response = self.client.post(
            reverse('images-list'),
            data=json.dumps(request_payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'][0], "You need to provide 'url' or 'file' parameter.",
        )
        request_payload = {'url': '228', 'file': self.image.picture.file}
        response = self.client.post(
            reverse('images-list'),
            data=request_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'][0], "You need to provide 'url' or 'file' parameter.",
        )

    def test_resize_parameters_validation(self):
        """Test resize method parameters validation."""
        url = reverse('images-resize', kwargs={'pk': self.image.id})
        response_without_parameters = self.client.post(
            url,
            data=json.dumps({}),
            content_type='application/json',
        )
        response_with_invalid_width = self.client.post(
            url,
            data=json.dumps({'width': 0}),
            content_type='application/json',
        )
        response_with_invalid_height = self.client.post(
            url,
            data=json.dumps({'height': 0}),
            content_type='application/json',
        )
        self.assertEqual(response_without_parameters.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_with_invalid_width.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_with_invalid_height.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response_without_parameters.data['error'][0],
            "You need to provide at least 'width' or 'height' parameter.",
        )
        self.assertEqual(
            response_with_invalid_width.data['error'][0],
            "'width' and 'height' parameters must be more than 0.",
        )
        self.assertEqual(
            response_with_invalid_height.data['error'][0],
            "'width' and 'height' parameters must be more than 0.",
        )

    def test_file_validation(self):
        """Test file validation."""
        url = 'https://psv4.userapi.com/c848120/u195413215/docs/d14/ba772e6e51dd/Strakhovka.docx'
        response_with_url = self.client.post(
            reverse('images-list'),
            data=json.dumps({'url': url}),
            content_type='application/json',
        )
        self.assertEqual(response_with_url.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response_with_url.data['error'][0],
            'Upload a valid image. The uploaded file is not an image or is corrupted.',
        )
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(b'Salam, brat')
            tmp_file.seek(0)
            response_with_file = self.client.post(
                reverse('images-list'),
                data={'file': tmp_file},
            )
            self.assertEqual(response_with_file.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response_with_file.data['file'][0],
                'Загрузите корректное изображение. Загруженный файл не является изображением, либо является испорченным.',  # Noqa: E501
            )

    @patch('requests.get')
    def test_download_request_validation(self, mock_request):
        """
        Test download request validation.

        Args:
            mock_request: Request mocker.
        """
        mock_response = requests.models.Response()
        mock_request.return_value = mock_response
        bad_statuses = [400, 403, 404, 500, 502, 503]
        for bad_status in bad_statuses:
            mock_response.status_code = bad_status
            response = self.client.post(
                reverse('images-list'),
                data=json.dumps({'url': 'https://murad_taxist.com/'}),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data['error'][0],
                "Can't download from this url. Download request returned {0} status code.".format(bad_status),  # Noqa: E501
            )


class MixinMethodsTest(ImageHandlerMixin, TestCase):
    """Test ImageHandlerMixin methods."""

    def setUp(self):
        """Prepare data for tests."""
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        self.image = ImageFactory.create()
        self.url = 'https://i.ibb.co/sJHms9y/ricardo.jpg'

    @classmethod
    def tearDownClass(cls):
        """Destroy directory in which files will upload during testing."""
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_new_image_instance_method(self):
        """Test create_new_image_instance method."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            instance = self.create_new_image_instance(tmp_file, url=self.url)
            self.assertIsInstance(instance, Image)
            self.assertEqual(instance.url, self.url)

    def test_save_image_method(self):
        """Test save_image method."""
        instance = self.save_image({'url': self.url})
        self.assertIsInstance(instance, Image)
        self.assertEqual(instance.url, self.url)

    def test_download_from_url_method(self):
        """Test download_from_url method."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            self.assertEqual(tmp_file.tell(), 0)
            self.download_from_url(self.url, tmp_file)
            self.assertNotEqual(tmp_file.tell(), 0)

    def test_resize_image_method(self):
        """Test resize_image method."""
        width, height = 2228, 2000
        new_instance = self.resize_image({'width': width, 'height': height}, self.image)
        self.assertIsInstance(new_instance, Image)
        with PILImage.open(new_instance.picture.file) as image:
            self.assertEqual(image.size, (width, height))

    def test_define_new_name_method(self):  # Noqa: WPS210
        """Test define_new_name method."""
        width, height = 2228, 2000
        name, ext = os.path.splitext(self.image.name)
        name_with_width_only = self.define_new_name({'width': width}, self.image.name)
        name_with_height_only = self.define_new_name({'height': height}, self.image.name)
        name_with_both = self.define_new_name({'width': width, 'height': height}, self.image.name)
        self.assertEqual(name_with_width_only, '{0}_{1}_0{2}'.format(name, width, ext))
        self.assertEqual(name_with_height_only, '{0}_0_{1}{2}'.format(name, height, ext))
        self.assertEqual(name_with_both, '{0}_{1}_{2}{3}'.format(name, width, height, ext))
