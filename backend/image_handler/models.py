from django.db import models


class Image(models.Model):
    name = models.CharField(blank=False)
    url = models.CharField(blank=True, null=True)
    picture = models.TextField(blank=False)
    width = models.PositiveIntegerField(blank=False)
    height = models.PositiveIntegerField(blank=False)
    parent_picture = models.CharField(blank=True, null=True)
