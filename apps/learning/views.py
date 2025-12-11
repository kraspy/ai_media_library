import django.contrib.auth.decorators
import django.views.decorators.http
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
        questions = self.object.concept.quiz_questions.all()

        score = 0
        total = questions.count()
        results = []

        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}')

            options = question.question_data.get('options', [])
            correct_index = question.question_data.get('correct_index')
            correct_answer = (
                options[correct_index]
                if options and correct_index is not None
                else None
            )
            is_correct = user_answer == correct_answer

            if is_correct:
                score += 1
            else:
                flashcard = Flashcard.objects.filter(
                    user=request.user, concept=question.concept
                ).first()

                if flashcard:
                    flashcard.interval = 1
                    flashcard.ease_factor = max(
                        1.3, flashcard.ease_factor - 0.2
                    )
                    flashcard.next_review = timezone.now().date()
                    flashcard.save()

            results.append(
                {
                    'question': question,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'explanation': question.question_data.get('explanation'),
                }
            )

        percentage = (score / total * 100) if total > 0 else 0
        passed = percentage >= 70

        if passed:
            self.object.is_completed = True
            self.object.save()

        return render(
            request,
            self.template_name,
            {
                'unit': self.object,
                'questions': questions,
                'results': results,
                'score': score,
                'total': total,
                'percentage': percentage,
                'passed': passed,
                'is_submitted': True,
            },
        )


class TutorChatView(LoginRequiredMixin, TemplateView):
    template_name = 'learning/tutor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.learning.models import Concept, StudyPlan, TutorChatSession

        if self.kwargs.get('create_new'):
            session = TutorChatSession.objects.create(
                user=self.request.user, title='New Chat'
            )
            context['session'] = session
        else:
            session_id = self.kwargs.get('pk')
            if session_id:
                session = get_object_or_404(
                    TutorChatSession, id=session_id, user=self.request.user
                )
            else:
                session = (
                    TutorChatSession.objects.filter(user=self.request.user)
                    .order_by('-updated_at')
                    .first()
                )
                if not session:
                    session = TutorChatSession.objects.create(
                        user=self.request.user
                    )

        context['session'] = session
        context['session_id'] = session.id
        context['chat_messages'] = session.messages.all()
        context['sessions'] = TutorChatSession.objects.filter(
            user=self.request.user
        ).order_by('-updated_at')

        context['active_plans'] = StudyPlan.objects.filter(
            user=self.request.user, status=StudyPlan.Status.ACTIVE
        ).order_by('-created_at')[:5]

        context['recent_concepts'] = (
            Concept.objects.filter(study_units__plan__user=self.request.user)
            .distinct()
            .order_by('-created_at')[:20]
        )

        return context

    def get(self, request, *args, **kwargs):
        if kwargs.get('create_new'):
            from apps.learning.models import TutorChatSession

            session = TutorChatSession.objects.create(user=request.user)
            return redirect('learning:tutor_session', pk=session.id)
        return super().get(request, *args, **kwargs)


class TutorAPIView(LoginRequiredMixin, View):
    def post(self, request):
        import json

        from django.http import JsonResponse

        from apps.learning.agents.tutor import TutorAgent
        from apps.learning.models import TutorChatSession

        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            session_id = data.get('session_id')

            if not user_message or not session_id:
                return JsonResponse({'error': 'Missing data'}, status=400)

            session = get_object_or_404(
                TutorChatSession, id=session_id, user=request.user
            )
            context_type = data.get('context_type')
            context_id = data.get('context_id')
            context_text = ''

            if context_type and context_id:
                from apps.learning.models import Concept, StudyPlan

                try:
                    if context_type == 'plan':
                        plan = StudyPlan.objects.get(
                            id=context_id, user=request.user
                        )
                        context_text = f"\n\n[Context: User is referring to Study Plan '{plan.topic.title}'. Plan ID: {plan.id}]"
                    elif context_type == 'concept':
                        concept = Concept.objects.get(id=context_id)
                        context_text = f"\n\n[Context: User is referring to Concept '{concept.title}'. Description: {concept.description}]"
                except Exception:
                    pass

            agent = TutorAgent()
            full_input = user_message + context_text

            response = agent.run(full_input, session_id=str(session.id))

            return JsonResponse({'response': response, 'status': 'success'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@django.views.decorators.http.require_POST
@django.contrib.auth.decorators.login_required
def delete_tutor_session(request, pk):
    from apps.learning.models import TutorChatSession

    session = get_object_or_404(TutorChatSession, id=pk, user=request.user)
    session.delete()
    return redirect('learning:tutor')
