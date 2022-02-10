import json
import shutil
import tempfile
from random import choice

import factory
from django.conf import settings
from django.urls import reverse
from images.factories import ImageFactory
from images.models import Image
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

    def test_get_detail_image_not_found(self):
        """Test getting non existence object."""
        url = reverse('images-detail', kwargs={'pk': 1488228})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy(self):
        """Test destroying object."""
        image_qs = Image.objects.filter(pk=self.image.id)
        self.assertTrue(image_qs.exists())
        url_delete = reverse('images-detail', kwargs={'pk': self.image.id})
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Image.DoesNotExist):
            Image.objects.get(pk=self.image.id)

    def test_destroy_not_found(self):
        """Test destroying non existence object."""
        url_delete = reverse('images-detail', kwargs={'pk': 1488228})
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        """Test updating object."""
        url_update = reverse('images-detail', kwargs={'pk': self.image.id})
        response = self.client.put(url_update)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update(self):
        """Test updating object."""
        url_patch = reverse('images-detail', kwargs={'pk': self.image.id})
        response = self.client.patch(url_patch)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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

    def test_resize_not_found(self):
        """Test resizing non existence object."""
        url = reverse('images-resize', kwargs={'pk': 1488228})
        response = self.client.post(
            url,
            data=json.dumps({'width': 228}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
