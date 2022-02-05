from django.urls import path
from images.views import ImageResizeView, ImagesViewSet, ImageView

app_name = 'images'
urlpatterns = [
    # path('<int:pk>/resize', ImageResizeView.as_view(), name='resize_image'),
    # path('<int:pk>/', DetailImageView.as_view()),
]

# urlpatterns = [
#     path('', ImageListView.as_view()),
#     # path('<int:pk>/', DetailImageView.as_view()),
# ]