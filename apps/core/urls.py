from django.urls import path

from .views import ProjectSettingsView

app_name = 'core'

urlpatterns = [
    path('settings/', ProjectSettingsView.as_view(), name='settings'),
]
