from django.views.generic import ListView

from .models import MediaItem


class MediaListView(ListView):
    model = MediaItem
    template_name = 'library/list.html'
    context_object_name = 'media_items'

    def get_queryset(self):
        return MediaItem.objects.filter(user=self.request.user).order_by(
            '-created_at'
        )
