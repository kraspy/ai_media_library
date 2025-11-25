from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import MediaItem


class MediaListView(ListView):
    model = MediaItem
    template_name = 'library/list.html'
    context_object_name = 'media_items'

    def get_queryset(self):
        return MediaItem.objects.filter(user=self.request.user).order_by(
            '-created_at'
        )


class MediaUploadView(CreateView):
    model = MediaItem
    fields = ['file', 'topic', 'tags']
    template_name = 'library/upload.html'
    success_url = reverse_lazy('library:list')

    def form_valid(self, form):
        files = self.request.FILES.getlist('file')
        topic = form.cleaned_data.get('topic')
        tags = form.cleaned_data.get('tags')

        for f in files:
            title = f.name

            ext = f.name.lower().split('.')[-1]
            if ext in ['mp4', 'mov', 'avi', 'mkv']:
                media_type = MediaItem.MediaType.VIDEO
            elif ext in ['mp3', 'wav', 'flac', 'm4a', 'ogg']:
                media_type = MediaItem.MediaType.AUDIO
            elif ext in ['jpg', 'jpeg', 'png', 'webp']:
                media_type = MediaItem.MediaType.IMAGE
            elif ext in ['txt', 'md']:
                media_type = MediaItem.MediaType.TEXT
            else:
                media_type = MediaItem.MediaType.TEXT

            instance = MediaItem.objects.create(
                user=self.request.user,
                file=f,
                title=title,
                media_type=media_type,
                topic=topic,
            )
            if tags:
                instance.tags.set(tags)

            from .tasks import (
                analyze_media,
            )

            analyze_media.delay(instance.id)

        return HttpResponseRedirect(self.success_url)


class MediaDetailView(DetailView):
    model = MediaItem
    template_name = 'library/detail.html'
    context_object_name = 'item'


class MediaUpdateView(UpdateView):
    model = MediaItem
    fields = ['title', 'topic', 'tags']
    template_name = 'library/update.html'
    success_url = reverse_lazy('library:list')


class MediaDeleteView(DeleteView):
    model = MediaItem
    template_name = 'library/delete.html'
    success_url = reverse_lazy('library:list')
