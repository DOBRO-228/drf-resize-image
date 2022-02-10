from django.db import models
from PIL import Image as PILImage


class Image(models.Model):
    url = models.TextField(blank=True, null=True)
    picture = models.ImageField(blank=False)
    parent_picture = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def name(self):
        """
        Define the name of the instance based on the picture file path.

        Returns:
            name(str): Instance name.
        """
        return self.picture.path.split('/').pop()

    @property
    def width(self):
        """
        Define the width of the instance based on the picture's width.

        Returns:
            width(int): Instance width.
        """
        with PILImage.open(self.picture.file) as image:
            return image.width

    @property
    def height(self):
        """
        Define the height of the instance based on the picture's height.

        Returns:
            height(int): Instance height.
        """
        with PILImage.open(self.picture.file) as image:
            return image.height

    def delete(self):
        """
        Delete image from the disk.

        Returns:
            Inherited delete method.
        """
        self.picture.delete()
        return super().delete()
