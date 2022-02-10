import os
import shutil
import tempfile

from django.conf import settings
from django.test import TestCase
from images.factories import ImageFactory
from images.mixins import ImageHandlerMixin
from images.models import Image
from PIL import Image as PILImage


class ImagesMixinMethodsTest(ImageHandlerMixin, TestCase):
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
