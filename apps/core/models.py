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
    concept_extraction_prompt = models.TextField(
        default='You are an expert educational analyst. Your goal is to extract key concepts from the provided text.\nExtract atomic concepts that are suitable for creating flashcards and study units.',
        help_text=_('System prompt for Concept Extraction Agent.'),
        verbose_name=_('Concept Extraction Prompt'),
    )
    plan_generation_prompt = models.TextField(
        default='You are an expert curriculum designer.\nCreate a logical, step-by-step study plan based on the provided concepts.\nOrder the units from simplest to most complex. Ensure dependencies are respected.',
        help_text=_('System prompt for Study Plan Generation Agent.'),
        verbose_name=_('Plan Generation Prompt'),
    )
    quiz_generation_prompt = models.TextField(
        default="You are an expert exam creator.\nGenerate multiple-choice questions to test the user's understanding of the concept.\nEnsure distractors (wrong answers) are plausible but incorrect.",
        help_text=_('System prompt for Quiz Generation Agent.'),
        verbose_name=_('Quiz Generation Prompt'),
    )
    tutor_prompt = models.TextField(
        default="You are a helpful AI Tutor. Use the available tools to answer the user's questions.",
        help_text=_('System prompt for Tutor Agent.'),
        verbose_name=_('Tutor Prompt'),
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
