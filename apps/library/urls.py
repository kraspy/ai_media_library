from django.urls import path

from .views import (
    MediaBulkActionView,
    MediaDeleteView,
    MediaDetailView,
    MediaListView,
    MediaUpdateView,
    MediaUploadView,
    TopicCreateView,
    TopicDeleteView,
    TopicListView,
    TopicUpdateView,
)

app_name = 'library'

urlpatterns = [
    path('', MediaListView.as_view(), name='list'),
    path('upload/', MediaUploadView.as_view(), name='upload'),
    path('detail/<int:pk>/', MediaDetailView.as_view(), name='detail'),
    path('update/<int:pk>/', MediaUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', MediaDeleteView.as_view(), name='delete'),
    path('bulk-action/', MediaBulkActionView.as_view(), name='bulk_action'),
    path('topics/', TopicListView.as_view(), name='topic_list'),
    path('topics/create/', TopicCreateView.as_view(), name='topic_create'),
    path(
        'topics/<slug:slug>/update/',
        TopicUpdateView.as_view(),
        name='topic_update',
    ),
    path(
        'topics/<slug:slug>/delete/',
        TopicDeleteView.as_view(),
        name='topic_delete',
    ),
]
