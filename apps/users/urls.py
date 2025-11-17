from django.urls import path

from .views import users_tmp_view

urlpatterns = [
    path('', users_tmp_view),
]
