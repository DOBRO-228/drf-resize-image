from images.views import ImagesViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'images', ImagesViewSet, basename='images')
