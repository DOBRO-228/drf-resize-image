from images.views import ImagesViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('images', ImagesViewSet, basename='images')
