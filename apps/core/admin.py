from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import ProjectSettings


@admin.register(ProjectSettings)
class ProjectSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ProjectSettings.objects.exists()

    def changelist_view(self, request, extra_context=None):
        obj, created = ProjectSettings.objects.get_or_create(pk=1)
        return redirect(
            reverse('admin:core_projectsettings_change', args=[obj.pk])
        )
