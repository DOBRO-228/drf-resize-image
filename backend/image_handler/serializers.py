from rest_framework import serializers
from image_handler.models import Image


class ImageSerializer(serializers.ModelSerializer):
    # name = models.CharField(blank=False)
    # url = models.CharField(blank=True, null=True)
    # picture = models.TextField(blank=False)
    # width = models.PositiveIntegerField(blank=False)
    # height = models.PositiveIntegerField(blank=False)
    # parent_picture = models.CharField(blank=True, null=True)

    class Meta:
        model = Image
        fields = ['id', 'name', 'url', 'picture', 'width', 'height', 'parent_picture']

    def create(self, validated_data):
        """
        Create and return a new `Image` instance, given the validated data.
        """
        return Image.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.url = validated_data.get('url', instance.url)
        instance.picture = validated_data.get('picture', instance.picture)
        instance.width = validated_data.get('width', instance.width)
        instance.height = validated_data.get('height', instance.height)
        instance.parent_picture = validated_data.get('parent_picture', instance.parent_picture)
        instance.save()
        return instance
