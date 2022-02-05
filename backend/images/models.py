from django.db import models


class Image(models.Model):
    url = models.TextField(blank=True, null=True)
    picture = models.ImageField(blank=False)
    width = models.PositiveIntegerField(blank=False)
    height = models.PositiveIntegerField(blank=False)
    parent_picture = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def name(self):
        """
        Define the name of the instance based on the picture file path.

        Returns:
            name(str): Instance name.
        """
        return self.picture.path.split('/').pop()

    def delete(self):
        """
        Delete image from the disk.

        Returns:
            Inherited delete method.
        """
        self.picture.delete()
        return super().delete()
