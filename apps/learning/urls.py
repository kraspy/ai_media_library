from django.urls import path

from .views import (
    LearningDashboardView,
    QuizView,
    StudyPlanDetailView,
    StudySessionView,
    TutorAPIView,
    TutorChatView,
    TutorContextUpdateView,
    delete_tutor_session,
)

app_name = 'learning'

urlpatterns = [
    path('', LearningDashboardView.as_view(), name='dashboard'),
    path('study/', StudySessionView.as_view(), name='study_session'),
    path('plan/<int:pk>/', StudyPlanDetailView.as_view(), name='plan_detail'),
    path('quiz/<int:pk>/', QuizView.as_view(), name='quiz'),
    path('tutor/', TutorChatView.as_view(), name='tutor'),
    path('tutor/<int:pk>/', TutorChatView.as_view(), name='tutor_session'),
    path(
        'tutor/create/',
        TutorChatView.as_view(),
        {'create_new': True},
        name='tutor_create',
    ),
    path(
        'tutor/<int:pk>/delete/',
        delete_tutor_session,
        name='tutor_delete',
    ),
    path('api/tutor/', TutorAPIView.as_view(), name='tutor_api'),
    path(
        'api/tutor/context/',
        TutorContextUpdateView.as_view(),
        name='tutor_context',
    ),
]
