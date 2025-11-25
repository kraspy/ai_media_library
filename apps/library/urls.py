from django.urls import path

from .views import (
    MediaListView,
    MediaUploadView,
)

app_name = 'library'

urlpatterns = [
    path('', MediaListView.as_view(), name='list'),
    path('upload/', MediaUploadView.as_view(), name='upload'),
]
