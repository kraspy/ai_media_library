from django.conf import settings
from django.db import models


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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
