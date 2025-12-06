from django.urls import path

from .views import (
    LearningDashboardView,
    QuizView,
    StudyPlanDetailView,
    StudySessionView,
    TutorAPIView,
    TutorChatView,
)

app_name = 'learning'

urlpatterns = [
    path('', LearningDashboardView.as_view(), name='dashboard'),
    path('study/', StudySessionView.as_view(), name='study_session'),
    path('plan/<int:pk>/', StudyPlanDetailView.as_view(), name='plan_detail'),
    path('quiz/<int:pk>/', QuizView.as_view(), name='quiz'),
    path('tutor/', TutorChatView.as_view(), name='tutor'),
    path('api/tutor/', TutorAPIView.as_view(), name='tutor_api'),
]
