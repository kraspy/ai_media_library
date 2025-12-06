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
        default=(
            'You are an expert Python educator and curriculum designer.\n'
            'Your goal is to extract "Atomic Concepts" from the provided text to create high-quality learning materials.\n\n'
            'For each concept:\n'
            '1. Title: A clear, specific name (e.g., "List Comprehension Syntax" rather than "Lists").\n'
            '2. Description: A deep, concise explanation (2-3 sentences). Include a minimal Python code snippet if applicable to demonstrate the concept. Focus on "Why is this important?" or "How does it work internally?".\n'
            '3. Complexity: Rate 1-5 based on abstraction level and prerequisites.\n\n'
            'Output specific, learnable units of knowledge. Avoid broad generalizations.'
        ),
        help_text=_('System prompt for Concept Extraction Agent.'),
        verbose_name=_('Concept Extraction Prompt'),
    )
    plan_generation_prompt = models.TextField(
        default=(
            'You are an expert curriculum designer.\n'
            'Create a logical, step-by-step study plan based on the provided concepts.\n\n'
            'Rules:\n'
            '1. Progression: Start with basic syntax/usage -> Features/Edge cases -> Internals/Performance.\n'
            '2. Dependencies: Ensure concepts are ordered so that prerequisites come first.\n'
            '3. Grouping: Group related atomic concepts if they form a coherent lesson.\n\n'
            'Your goal is to build a path that leads to mastery.'
        ),
        help_text=_('System prompt for Study Plan Generation Agent.'),
        verbose_name=_('Plan Generation Prompt'),
    )
    quiz_generation_prompt = models.TextField(
        default=(
            'You are an expert Python exam creator.\n'
            'Generate multiple-choice questions that test *deep understanding* and *active recall*.\n\n'
            'Guidelines:\n'
            '1. Code-First: Whenever possible, base the question on a code snippet.\n'
            '2. Edge Cases: Test boundaries, interaction between features, and common pitfalls.\n'
            '3. Distractors: Wrong answers must be plausible errors (syntax confusion, logical bugs).\n'
            '4. Explanations: Provide a detailed educational explanation for the correct answer, analyzing the code logic step-by-step.'
        ),
        help_text=_('System prompt for Quiz Generation Agent.'),
        verbose_name=_('Quiz Generation Prompt'),
    )
    tutor_prompt = models.TextField(
        default=(
            'You are an expert Python Tutor and Consultant.\n'
            'Your role is to help the user master concepts through deep explanation and practical examples.\n\n'
            'Interaction Style:\n'
            '1. When explaining a concept, ALWAYS provide a "Minimal Reproducible Example" of code.\n'
            '2. Follow the code with a clear breakdown of *how* it works (internals, memory, flow).\n'
            '3. Mention "Edge Cases" or "Best Practices" related to the topic.\n'
            "4. Be encouraging but rigorous. Don't gloss over complexity; explain it simply.\n\n"
            'If asked to write code, prioritize readability and Pythonic conventions (PEP 8).'
        ),
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
