from django.contrib import admin

from .models import Concept


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_item', 'complexity', 'created_at')
    list_filter = ('complexity', 'created_at')
    search_fields = ('title', 'description')
