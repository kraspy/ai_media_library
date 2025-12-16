from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class Topic(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name=_('User'),
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtopics',
        verbose_name=_('Parent Topic'),
    )
    title = models.CharField(_('Title'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        unique_together = ('user', 'slug')
        ordering = ['title']
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')

    def __str__(self):
        if self.parent:
            return f'{self.parent.title} -> {self.title}'
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Topic.objects.filter(user=self.user, slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class MediaItem(models.Model):
    class MediaType(models.TextChoices):
        AUDIO = 'audio', _('Audio')
        VIDEO = 'video', _('Video')
        IMAGE = 'image', _('Image')
        TEXT = 'text', _('Text')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='media_items',
        verbose_name=_('User'),
    )
    title = models.CharField(_('Title'), max_length=255)
    file = models.FileField(_('File'), upload_to='uploads/%Y/%m/%d/')
    media_type = models.CharField(
        _('Media Type'),
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.TEXT,
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    processing_step = models.CharField(
        _('Processing Step'), max_length=255, blank=True, null=True
    )
    transcription = models.TextField(_('Transcription'), blank=True)
    summary = models.TextField(_('Summary'), blank=True)
    error_log = models.TextField(
        _('Error Log'),
        blank=True,
        help_text=_('Stores stack traces for failed tasks.'),
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='media_items',
        verbose_name=_('Topic'),
    )
    tags = TaggableManager(_('Tags'), blank=True)

    class Meta:
        verbose_name = _('Media Item')
        verbose_name_plural = _('Media Items')

    def __str__(self):
        return self.title
