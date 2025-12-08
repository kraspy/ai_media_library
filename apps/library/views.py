from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .models import MediaItem
from .tasks import analyze_media


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
        supported_extensions = [
            'mp4',
            'mov',
            'avi',
            'mkv',
            'mp3',
            'wav',
            'flac',
            'm4a',
            'ogg',
            'jpg',
            'jpeg',
            'png',
            'webp',
            'txt',
            'md',
        ]

        from django.contrib import messages
        from django.utils.translation import gettext as _

        for f in files:
            ext = f.name.lower().split('.')[-1]
            if ext not in supported_extensions:
                messages.error(
                    self.request,
                    _(
                        'File "%(filename)s" has an unsupported extension: .%(ext)s'
                    )
                    % {'filename': f.name, 'ext': ext},
                )
                return HttpResponseRedirect(self.success_url)

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
                continue

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

        messages.success(self.request, _('Files uploaded successfully.'))
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


class MediaBulkActionView(LoginRequiredMixin, View):
    def post(self, request):
        action = request.POST.get('action')
        media_ids = request.POST.getlist('media_ids')

        if not media_ids:
            return redirect('library:list')

        queryset = MediaItem.objects.filter(id__in=media_ids)

        if action == 'delete':
            count = queryset.count()
            queryset.delete()

        elif action == 'reanalyze':
            for item in queryset:
                item.status = MediaItem.Status.PENDING
                item.transcription = ''
                item.summary = ''
                item.error_log = ''
                item.save()
                analyze_media.delay(item.id)

        return redirect('library:list')


class MediaDeleteView(DeleteView):
    model = MediaItem
    template_name = 'library/delete.html'
    success_url = reverse_lazy('library:list')
