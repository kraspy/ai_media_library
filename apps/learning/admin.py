from django.contrib import admin

from .models import Concept, Flashcard, StudyPlan, StudyUnit


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_item', 'complexity', 'created_at')
    list_filter = ('complexity', 'created_at')
    search_fields = ('title', 'description')


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = (
        'front',
        'user',
        'concept',
        'reps',
        'interval',
        'next_review',
    )
    list_filter = ('next_review', 'reps')
    search_fields = ('front', 'back')


class StudyUnitInline(admin.TabularInline):
    model = StudyUnit
    extra = 0


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'media_item', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [StudyUnitInline]
