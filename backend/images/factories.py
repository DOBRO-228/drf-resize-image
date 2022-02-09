import factory
from faker import Faker
from images.models import Image


class ImageFactory(factory.django.DjangoModelFactory):
    """Image factory."""

    class Meta:
        model = Image

    url = None
    picture = factory.django.ImageField(
        filename=factory.Sequence(lambda elem: Faker().file_name(category='image')),
        width=factory.Faker('pyint', min_value=1, max_value=1000),
        height=factory.Faker('pyint', min_value=1, max_value=1000),
    )
    parent_picture = None
