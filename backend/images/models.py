from urllib.parse import urljoin

from django.conf import settings
from django.db import models


class Image(models.Model):
    name = models.TextField(blank=False)
    url = models.TextField(blank=True, null=True)
    picture = models.FileField(null=False, blank=False)
    width = models.PositiveIntegerField(blank=False)
    height = models.PositiveIntegerField(blank=False)
    parent_picture = models.TextField(blank=True, null=True)

