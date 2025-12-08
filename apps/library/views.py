from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .models import MediaItem, Topic
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
        files = self.request.FILES.getlist('file')
        topic = form.cleaned_data.get('topic')
        tags = form.cleaned_data.get('tags')

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

            try:
                analyze_media.delay(instance.id)
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(
                    f'Failed to schedule analysis for {instance.id}: {e}'
                )
                messages.warning(
                    self.request,
                    _(
                        'File "%(filename)s" uploaded, but analysis could not be started due to an API error.'
                    )
                    % {'filename': f.name},
                )

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
            from django.contrib import messages
            from django.utils.translation import gettext as _

            error_count = 0
            for item in queryset:
                item.status = MediaItem.Status.PENDING
                item.transcription = ''
                item.summary = ''
                item.error_log = ''
                item.save()
                try:
                    analyze_media.delay(item.id)
                except Exception:
                    error_count += 1

            if error_count > 0:
                messages.warning(
                    request,
                    _(
                        'Analysis re-started, but %(count)d items failed to schedule due to API error.'
                    )
                    % {'count': error_count},
                )
            else:
                messages.success(
                    request, _('Analysis re-started for selected items.')
                )

        return redirect('library:list')


class MediaDeleteView(DeleteView):
    model = MediaItem
    template_name = 'library/delete.html'
    success_url = reverse_lazy('library:list')


class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'library/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.filter(user=self.request.user).order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topics = list(self.get_queryset())
        topic_dict = {t.id: {'node': t, 'children': []} for t in topics}
        root_nodes = []

        for t in topics:
            if t.parent_id:
                if t.parent_id in topic_dict:
                    topic_dict[t.parent_id]['children'].append(
                        topic_dict[t.id]
                    )
            else:
                root_nodes.append(topic_dict[t.id])

        def sort_tree(nodes):
            nodes.sort(key=lambda x: x['node'].title.lower())
            for node in nodes:
                sort_tree(node['children'])

        sort_tree(root_nodes)
        context['topic_tree'] = root_nodes
        return context


class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topic
    fields = ['title', 'parent']
    template_name = 'library/topic_form.html'
    success_url = reverse_lazy('library:topic_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['parent'].queryset = Topic.objects.filter(
            user=self.request.user
        )
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Topic created successfully.'))
        return super().form_valid(form)


class TopicUpdateView(LoginRequiredMixin, UpdateView):
    model = Topic
    fields = ['title', 'parent']
    template_name = 'library/topic_form.html'
    success_url = reverse_lazy('library:topic_list')
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Topic.objects.filter(user=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        qs = Topic.objects.filter(user=self.request.user).exclude(
            id=self.object.id
        )
        qs = Topic.objects.filter(user=self.request.user).exclude(
            id=self.object.id
        )
        form.fields['parent'].queryset = qs
        return form

    def form_valid(self, form):
        messages.success(self.request, _('Topic updated successfully.'))
        return super().form_valid(form)


class TopicDeleteView(LoginRequiredMixin, DeleteView):
    model = Topic
    template_name = 'library/topic_delete.html'
    success_url = reverse_lazy('library:topic_list')
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Topic.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _('Topic deleted successfully.'))
        return super().form_valid(form)
