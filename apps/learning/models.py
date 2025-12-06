from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.library.models import MediaItem, Topic


class Concept(models.Model):
    """
    An atomic unit of knowledge extracted from a MediaItem.
    """

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    media_item = models.ForeignKey(
        MediaItem,
        on_delete=models.CASCADE,
        related_name='concepts',
        verbose_name=_('Media Item'),
    )
    complexity = models.PositiveIntegerField(
        _('Complexity'), default=1, help_text=_('Complexity level (1-5)')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Concept')
        verbose_name_plural = _('Concepts')

    def __str__(self):
        return self.title


class Flashcard(models.Model):
    """
    An SRS card for spaced repetition.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='flashcards',
        verbose_name=_('User'),
    )
    concept = models.ForeignKey(
        Concept,
        on_delete=models.CASCADE,
        related_name='flashcards',
        verbose_name=_('Concept'),
    )
    front = models.TextField(_('Front'), help_text=_('Question or front side'))
    back = models.TextField(_('Back'), help_text=_('Answer or back side'))

    # SRS Fields
    reps = models.PositiveIntegerField(
        _('Repetitions'), default=0, help_text=_('Number of repetitions')
    )
    interval = models.PositiveIntegerField(
        _('Interval'), default=0, help_text=_('Days until next review')
    )
    ease_factor = models.FloatField(
        _('Ease Factor'), default=2.5, help_text=_('Easiness factor')
    )
    last_review = models.DateField(_('Last Review'), null=True, blank=True)
    next_review = models.DateField(_('Next Review'), default=timezone.now)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Flashcard')
        verbose_name_plural = _('Flashcards')

    def __str__(self):
        return f'Flashcard: {self.front[:50]}...'


class StudyPlan(models.Model):
    """
    A container for a user's learning journey.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        ARCHIVED = 'archived', _('Archived')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_plans',
        verbose_name=_('User'),
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_plans',
        verbose_name=_('Topic'),
    )
    media_item = models.ForeignKey(
        MediaItem,
        on_delete=models.CASCADE,
        related_name='study_plans',
        verbose_name=_('Media Item'),
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Study Plan')
        verbose_name_plural = _('Study Plans')

    def __str__(self):
        return f'Plan for {self.user.username} ({self.created_at.date()})'


class StudyUnit(models.Model):
    """
    A specific lesson/module within a plan.
    """

    plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name=_('Study Plan'),
    )
    concept = models.ForeignKey(
        Concept,
        on_delete=models.CASCADE,
        related_name='study_units',
        verbose_name=_('Concept'),
    )
    order = models.PositiveIntegerField(_('Order'), default=0)
    is_completed = models.BooleanField(_('Is Completed'), default=False)

    class Meta:
        ordering = ['order']
        verbose_name = _('Study Unit')
        verbose_name_plural = _('Study Units')

    def __str__(self):
        return f'{self.order}. {self.concept.title}'


class QuizQuestion(models.Model):
    """
    A generated quiz question.
    """

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'multiple_choice', _('Multiple Choice')
        OPEN = 'open', _('Open Answer')

    concept = models.ForeignKey(
        Concept,
        on_delete=models.CASCADE,
        related_name='quiz_questions',
        verbose_name=_('Concept'),
    )
    question_data = models.JSONField(
        _('Question Data'),
        help_text=_(
            'JSON structure with question, options, correct_answer, explanation'
        ),
    )
    question_type = models.CharField(
        _('Question Type'),
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Quiz Question')
        verbose_name_plural = _('Quiz Questions')

    def __str__(self):
        return f'Quiz for {self.concept.title}'


class TutorChatSession(models.Model):
    """
    A chat session with the AI Tutor.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutor_sessions',
        verbose_name=_('User'),
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Tutor Chat Session')
        verbose_name_plural = _('Tutor Chat Sessions')
        ordering = ['-updated_at']

    def __str__(self):
        return f'Session {self.id} for {self.user.username}'


class TutorChatMessage(models.Model):
    """
    A message in a TutorChatSession.
    """

    class Role(models.TextChoices):
        USER = 'user', _('User')
        ASSISTANT = 'assistant', _('Assistant')

    session = models.ForeignKey(
        TutorChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Session'),
    )
    role = models.CharField(
        _('Role'), max_length=10, choices=Role.choices, default=Role.USER
    )
    content = models.TextField(_('Content'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}...'
