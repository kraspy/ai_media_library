from django.contrib import admin

from .models import MediaItem, Topic
from .tasks import analyze_media, summarize_media


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'status', 'created_at', 'topic')
    list_filter = ('status', 'media_type', 'created_at', 'topic', 'tags')
    search_fields = ('title', 'transcription', 'summary')
    actions = ['analyze_selected', 'summarize_selected']

    @admin.action(description='Analyze selected items')
    def analyze_selected(self, request, queryset):
        for item in queryset:
            analyze_media.delay(item.id)
        self.message_user(
            request, f'Started analysis for {queryset.count()} items.'
        )

    @admin.action(description='Summarize selected items')
    def summarize_selected(self, request, queryset):
        for item in queryset:
            summarize_media.delay(item.id)
        self.message_user(
            request, f'Started summarization for {queryset.count()} items.'
        )

    readonly_fields = ('created_at', 'transcription', 'summary')
