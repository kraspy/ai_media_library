from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, TemplateView, View

from apps.learning.models import Flashcard, StudyPlan, StudyUnit
from apps.learning.services.srs import calculate_next_review


class LearningDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'learning/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        context['cards_due_count'] = Flashcard.objects.filter(
            user=user, next_review__lte=today
        ).count()

        context['active_plans'] = StudyPlan.objects.filter(
            user=user, status=StudyPlan.Status.ACTIVE
        ).annotate(
            total_units=Count('units'),
            completed_units=Count('units', filter=Q(units__is_completed=True)),
        )

        context['recent_activity'] = StudyUnit.objects.filter(
            plan__user=user, is_completed=True
        ).order_by('-plan__created_at')[:5]

        return context


class StudyPlanDetailView(LoginRequiredMixin, DetailView):
    model = StudyPlan
    template_name = 'learning/plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return StudyPlan.objects.filter(user=self.request.user)


class StudySessionView(LoginRequiredMixin, View):
    template_name = 'learning/study_session.html'

    def get(self, request):
        today = timezone.now().date()
        cards = Flashcard.objects.filter(
            user=request.user, next_review__lte=today
        ).order_by('next_review')

        if not cards.exists():
            return render(request, 'learning/session_complete.html')

        card = cards.first()
        return render(
            request,
            self.template_name,
            {'card': card, 'cards_count': cards.count()},
        )

    def post(self, request):
        card_id = request.POST.get('card_id')
        quality = int(request.POST.get('quality'))

        card = get_object_or_404(Flashcard, id=card_id, user=request.user)

        new_interval, new_ease = calculate_next_review(
            quality, card.interval, card.ease_factor, card.reps
        )

        card.interval = new_interval
        card.ease_factor = new_ease
        card.reps += 1
        card.last_review = timezone.now().date()
        card.next_review = card.last_review + timezone.timedelta(
            days=new_interval
        )
        card.save()

        return redirect('learning:study_session')


class QuizView(LoginRequiredMixin, DetailView):
    model = StudyUnit
    template_name = 'learning/quiz.html'
    context_object_name = 'unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.concept.quiz_questions.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_completed = True
        self.object.save()
        return redirect('learning:plan_detail', pk=self.object.plan.id)
