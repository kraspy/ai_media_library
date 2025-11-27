from django.db import models

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
