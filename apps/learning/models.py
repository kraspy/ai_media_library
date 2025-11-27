from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.library.models import MediaItem


class Concept(models.Model):
    """
    An atomic unit of knowledge extracted from a MediaItem.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    media_item = models.ForeignKey(
        MediaItem, on_delete=models.CASCADE, related_name='concepts'
    )
    complexity = models.PositiveIntegerField(
        default=1, help_text='Complexity level (1-5)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

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
    )
    concept = models.ForeignKey(
        Concept,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flashcards',
    )
    front = models.TextField(help_text='Question or front side')
    back = models.TextField(help_text='Answer or back side')

    # SRS Fields
    reps = models.PositiveIntegerField(
        default=0, help_text='Number of repetitions'
    )
    interval = models.PositiveIntegerField(
        default=0, help_text='Days until next review'
    )
    ease_factor = models.FloatField(default=2.5, help_text='Easiness factor')
    last_review = models.DateField(null=True, blank=True)
    next_review = models.DateField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Flashcard: {self.front[:50]}...'
