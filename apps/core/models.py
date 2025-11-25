from django.core.cache import cache
from django.db import models


class ProjectSettings(models.Model):
    class TranscriptionEngine(models.TextChoices):
        OPENAI = 'openai', 'OpenAI Whisper'
        WHISPERX = 'whisperx', 'WhisperX (Local)'
        T_ONE = 't_one', 'T-One (Local)'

    class LLMProvider(models.TextChoices):
        OPENAI = 'openai', 'OpenAI'
        DEEPSEEK = 'deepseek', 'DeepSeek'

    transcription_engine = models.CharField(
        max_length=20,
        choices=TranscriptionEngine.choices,
        default=TranscriptionEngine.WHISPERX,
        help_text='Select transcription engine.',
    )
    llm_provider = models.CharField(
        max_length=20,
        choices=LLMProvider.choices,
        default=LLMProvider.OPENAI,
        help_text='Select LLM provider.',
    )
    summarization_prompt = models.TextField(
        default='Please provide a concise summary of the following text.',
        help_text='System prompt for Summarization.',
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
        return 'Settings'

    class Meta:
        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'
