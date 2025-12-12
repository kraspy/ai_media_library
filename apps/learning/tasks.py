import asyncio
import logging
import traceback

from asgiref.sync import async_to_sync
from celery import shared_task
from django.db import transaction

from apps.learning.models import (
    Concept,
    Flashcard,
    QuizQuestion,
    StudyPlan,
    StudyUnit,
)
from apps.learning.services.ai_service import AIService
from apps.library.models import MediaItem

logger = logging.getLogger(__name__)


@shared_task
def generate_content_from_media(media_item_id):
    """
    Orchestrates the generation of learning content from a processed MediaItem.
    1. Extract Concepts
    2. Generate Study Plan
    3. Generate Quizzes
    4. Generate Flashcards
    """
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        logger.info(f'Starting content generation for {media_item.title}')

        media_item.processing_step = 'Extracting Concepts...'
        media_item.status = MediaItem.Status.PROCESSING
        media_item.save(update_fields=['processing_step', 'status'])

        ai_service = AIService()

        text_content = media_item.summary or media_item.transcription
        if not text_content:
            logger.warning(f'No text content found for {media_item.title}')
            return

        topic_context = ''
        if media_item.topic:
            topic_context = media_item.topic.title
            if media_item.topic.parent:
                topic_context = (
                    f'{media_item.topic.parent.title} -> {topic_context}'
                )

        logger.info('Extracting concepts...')
        concept_list = ai_service.extract_concepts(text_content, topic_context)

        saved_concepts = []
        with transaction.atomic():
            for schema in concept_list.concepts:
                concept, created = Concept.objects.get_or_create(
                    title=schema.title,
                    media_item=media_item,
                    defaults={
                        'description': schema.description,
                        'complexity': schema.complexity,
                    },
                )
                saved_concepts.append(concept)

                Flashcard.objects.get_or_create(
                    user=media_item.user,
                    concept=concept,
                    defaults={
                        'front': concept.title,
                        'back': concept.description,
                    },
                )

        logger.info('Generating study plan...')
        media_item.processing_step = 'Generating Study Plan...'
        media_item.save(update_fields=['processing_step'])

        plan_schema = ai_service.generate_study_plan(
            saved_concepts, media_item.title, topic_context
        )

        with transaction.atomic():
            study_plan = StudyPlan.objects.create(
                user=media_item.user,
                topic=media_item.topic,
                media_item=media_item,
                status=StudyPlan.Status.ACTIVE,
            )

            for unit_schema in plan_schema.units:
                concept = next(
                    (
                        c
                        for c in saved_concepts
                        if c.title == unit_schema.concept_title
                    ),
                    None,
                )
                if concept:
                    StudyUnit.objects.create(
                        plan=study_plan,
                        concept=concept,
                        order=unit_schema.order,
                        is_completed=False,
                    )

        logger.info('Generating quizzes...')
        media_item.processing_step = 'Generating Quizzes...'
        media_item.save(update_fields=['processing_step'])

        async def _generate_quizzes_concurrently():
            semaphore = asyncio.Semaphore(5)

            async def generate_with_limit(concept):
                async with semaphore:
                    try:
                        quiz_schema = await ai_service.generate_quiz_async(
                            concept_title=concept.title,
                            concept_description=concept.description,
                            context_text=text_content[:2000],
                            topic_context=topic_context,
                        )
                        return concept, quiz_schema
                    except Exception as e:
                        logger.error(
                            f'Failed to generate quiz for concept {concept.title}: {e}'
                        )
                        return concept, None

            tasks = [generate_with_limit(c) for c in saved_concepts]
            results = await asyncio.gather(*tasks)
            return results

        results = async_to_sync(_generate_quizzes_concurrently)()

        with transaction.atomic():
            for concept, quiz_schema in results:
                if quiz_schema:
                    for question_schema in quiz_schema.questions:
                        QuizQuestion.objects.create(
                            concept=concept,
                            question_data=question_schema.model_dump(),
                            question_type=QuizQuestion.QuestionType.MULTIPLE_CHOICE,
                        )

        media_item.processing_step = None
        media_item.status = MediaItem.Status.COMPLETED
        media_item.save(update_fields=['processing_step', 'status'])

        logger.info(f'Content generation completed for {media_item.title}')

    except Exception as e:
        logger.error(f'Error generating content for {media_item_id}: {e}')
        traceback.print_exc()
