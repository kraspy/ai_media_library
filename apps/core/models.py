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
    summarize_prompt_default = (
        'Analyze the user-provided text. Think step-by-step:\n'
        '1. IDENTIFY the main topic and the type of material (e.g., lecture, code documentation, article).\n'
        '2. EXTRACT the key arguments, core concepts, and critical details.\n'
        '3. DETERMINE the target audience and the depth of the content.\n\n'
        'Then, write a high-quality summary that:\n'
        '- Starts with a clear context statement.\n'
        '- Synthesizes the information rather than just listing it.\n'
        '- Highlights the "individual features" or nuances of the material.\n'
        '- Is informative, structured, and easy to read.'
    )
    summarization_prompt = models.TextField(
        default=summarize_prompt_default,
        help_text=_('System prompt for Summarization.'),
        verbose_name=_('Summarization Prompt'),
    )
    concept_extraction_prompt = models.TextField(
        default=(
            'You are an expert Educator and Curriculum Designer.\n'
            'Your goal is to extract "Atomic Concepts" from the provided text to create high-quality learning materials.\n\n'
            'For each concept:\n'
            '1. Title: A clear, specific name (e.g., "Newton\'s Second Law" rather than "Physics").\n'
            '2. Description: A deep, concise explanation (2-3 sentences). Focus on "Why is this important?" or "How does it work internally?".\n'
            '3. Complexity: Rate 1-5 based on abstraction level and prerequisites.\n\n'
            'Output specific, learnable units of knowledge. Avoid broad generalizations.'
        ),
        help_text=_('System prompt for Concept Extraction Agent.'),
        verbose_name=_('Concept Extraction Prompt'),
    )
    plan_generation_prompt = models.TextField(
        default=(
            'You are an expert Curriculum Designer.\n'
            'Create a logical, step-by-step study plan based on the provided concepts.\n\n'
            'Rules:\n'
            '1. Progression: Start with foundations -> Core mechanisms -> Advanced applications.\n'
            '2. Dependencies: Ensure concepts are ordered so that prerequisites come first.\n'
            '3. Grouping: Group related atomic concepts if they form a coherent lesson.\n\n'
            'Your goal is to build a path that leads to mastery.'
        ),
        help_text=_('System prompt for Study Plan Generation Agent.'),
        verbose_name=_('Plan Generation Prompt'),
    )
    quiz_generation_prompt = models.TextField(
        default=(
            'You are an expert Exam Creator.\n'
            'Generate multiple-choice questions that test *deep understanding* and *active recall*.\n\n'
            'Guidelines:\n'
            '1. Context-First: Base questions on the specific nuances of the material.\n'
            '2. Hard Skills: Test specific details, logic, or mechanisms described.\n'
            '3. Distractors: Wrong answers must be plausible errors (misconceptions, logical traps).\n'
            '4. Explanations: Provide a detailed educational explanation for the correct answer.'
        ),
        help_text=_('System prompt for Quiz Generation Agent.'),
        verbose_name=_('Quiz Generation Prompt'),
    )
    tutor_prompt = models.TextField(
        default=(
            'You are an expert Tutor and Consultant.\n'
            'Your role is to help the user master concepts through deep explanation and practical examples.\n\n'
            'Interaction Style:\n'
            '1. When explaining, use analogies and concrete examples relevant to the topic.\n'
            '2. Break down complex ideas into constituent parts.\n'
            '3. Mention "Edge Cases" or "Common Pitfalls" related to the topic.\n'
            "4. Be encouraging but rigorous. Don't gloss over complexity; explain it simply.\n"
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
