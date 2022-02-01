from django.urls import path
from images.views import DetailImageView, ImagesViewSet, ImageView

app_name = 'images'
urlpatterns = [
    # path('', ImageView.as_view()),
    # path('<int:pk>/', DetailImageView.as_view()),
]

# urlpatterns = [
#     path('', ImageListView.as_view()),
#     # path('<int:pk>/', DetailImageView.as_view()),
# ]