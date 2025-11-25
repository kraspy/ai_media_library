from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .models import ProjectSettings


class ProjectSettingsView(LoginRequiredMixin, UpdateView):
    model = ProjectSettings
    fields = [
        'transcription_engine',
        'llm_provider',
        'chat_prompt',
        'summarization_prompt',
    ]
    template_name = 'core/settings.html'
    success_url = reverse_lazy('core:settings')

    def get_object(self):
        return ProjectSettings.load()
