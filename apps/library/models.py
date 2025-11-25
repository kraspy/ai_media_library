from django.conf import settings
from django.db import models
from taggit.managers import TaggableManager


class Topic(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topics',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtopics',
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'slug')
        ordering = ['title']

    def __str__(self):
        if self.parent:
            return f'{self.parent.title} -> {self.title}'
        return self.title


class MediaItem(models.Model):
    class MediaType(models.TextChoices):
        AUDIO = 'audio', 'Audio'
        VIDEO = 'video', 'Video'
        IMAGE = 'image', 'Image'
        TEXT = 'text', 'Text'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='media_items',
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.TEXT,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    transcription = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    error_log = models.TextField(
        blank=True, help_text='Stores stack traces for failed tasks.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='media_items',
    )
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title
