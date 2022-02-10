import json
import shutil
import tempfile

import requests
from django.conf import settings
from django.urls import reverse
from images.factories import ImageFactory
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase


class ImagesValidationTest(APITestCase):
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
        url = 'https://file38.gofile.io/download/a9d85056-1ac6-47a4-bf1a-df575d5e4cec/SQL.txt'
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
