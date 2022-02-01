from images.views import ImageListView, ImagesViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'images', ImageListView, basename='get_images')
router.register(r'images', ImagesViewSet, basename='images')
