from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProjectSettings(models.Model):
    class TranscriptionEngine(models.TextChoices):
        OPENAI = 'openai', 'OpenAI Whisper'
        WHISPERX = 'whisperx', 'WhisperX (Local)'

    class LLMProvider(models.TextChoices):
        OPENAI = 'openai', 'OpenAI'
        DEEPSEEK = 'deepseek', 'DeepSeek'

    transcription_engine = models.CharField(
        max_length=20,
        choices=TranscriptionEngine.choices,
        default=TranscriptionEngine.WHISPERX,
        help_text=_('Select transcription engine.'),
        verbose_name=_('Transcription Engine'),
    )
    llm_provider = models.CharField(
        max_length=20,
        choices=LLMProvider.choices,
        default=LLMProvider.OPENAI,
        help_text=_('Select LLM provider.'),
        verbose_name=_('LLM Provider'),
    )
    summarization_prompt = models.TextField(
        default='Please provide a concise summary of the following text.',
        help_text=_('System prompt for Summarization.'),
        verbose_name=_('Summarization Prompt'),
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.set('project_settings', self)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj = cache.get('project_settings')
        if obj is None:
            obj, created = cls.objects.get_or_create(pk=1)
            cache.set('project_settings', obj)
        return obj

    def __str__(self):
        return str(_('Settings'))

    class Meta:
        verbose_name = _('Settings')
        verbose_name_plural = _('Settings')
