from django.urls import path

from .views import (
    MediaDeleteView,
    MediaDetailView,
    MediaListView,
    MediaUpdateView,
    MediaUploadView,
)

app_name = 'library'

urlpatterns = [
    path('', MediaListView.as_view(), name='list'),
    path('upload/', MediaUploadView.as_view(), name='upload'),
    path('detail/<int:pk>/', MediaDetailView.as_view(), name='detail'),
    path('update/<int:pk>/', MediaUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', MediaDeleteView.as_view(), name='delete'),
]
