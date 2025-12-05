from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .models import ProjectSettings


class ProjectSettingsView(LoginRequiredMixin, UpdateView):
    model = ProjectSettings
    fields = [
        'transcription_engine',
        'llm_provider',
        'summarization_prompt',
        'concept_extraction_prompt',
        'plan_generation_prompt',
        'quiz_generation_prompt',
        'tutor_prompt',
    ]
    template_name = 'core/settings.html'
    success_url = reverse_lazy('core:settings')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            if isinstance(
                field.widget, (forms.TextInput, forms.Textarea, forms.Select)
            ):
                attrs = field.widget.attrs
                attrs['class'] = attrs.get('class', '') + ' form-control'
        return form

    def get_object(self):
        return ProjectSettings.load()
