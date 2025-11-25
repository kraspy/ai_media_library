import gc
import logging
import traceback
from pathlib import Path

import torch
import whisperx
from celery import shared_task
from django.conf import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI

from apps.core.models import ProjectSettings

from .models import MediaItem

logger = logging.getLogger(__name__)


@shared_task
def analyze_media(media_item_id):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        media_item.status = MediaItem.Status.PROCESSING
        media_item.save()

        project_settings = ProjectSettings.load()
        engine = project_settings.transcription_engine
        transcription_text = ''

        logger.info(
            f'Starting processing for {media_item.id} ({media_item.media_type})'
        )

        audio_path = media_item.file.path

        if media_item.media_type == MediaItem.MediaType.VIDEO:
            from apps.library.services.media_processing import (
                cut_audio_from_video,
            )

            audio_path = cut_audio_from_video(Path(media_item.file.path))
            logger.info(f'Extracted audio to {audio_path}')

        if media_item.media_type == MediaItem.MediaType.IMAGE:
            from apps.library.services.media_processing import perform_ocr

            transcription_text = perform_ocr(Path(media_item.file.path))

        elif media_item.media_type == MediaItem.MediaType.TEXT:
            with open(
                media_item.file.path, 'r', encoding='utf-8', errors='ignore'
            ) as f:
                transcription_text = f.read()

        elif media_item.media_type in [
            MediaItem.MediaType.AUDIO,
            MediaItem.MediaType.VIDEO,
        ]:
            logger.info(f'Transcribing audio from {audio_path} using {engine}')

            if engine == ProjectSettings.TranscriptionEngine.WHISPERX:
                device = settings.WHISPER_DEVICE
                batch_size = 16
                compute_type = settings.WHISPER_COMPUTE_TYPE

                model = whisperx.load_model(
                    settings.WHISPER_MODEL,
                    device,
                    compute_type=compute_type,
                )

                audio = whisperx.load_audio(str(audio_path))
                result = model.transcribe(audio, batch_size=batch_size)

                del model
                gc.collect()
                if device == 'cuda':
                    torch.cuda.empty_cache()

                for segment in result['segments']:
                    transcription_text += segment['text'] + '\n'

            elif engine == ProjectSettings.TranscriptionEngine.T_ONE:
                from tone import StreamingCTCPipeline, read_audio

                audio = read_audio(str(audio_path))
                pipeline = StreamingCTCPipeline.from_hugging_face()
                phrases = pipeline.forward_offline(audio)
                transcription_text = (
                    ' '.join([p.text for p in phrases])
                    if phrases and hasattr(phrases[0], 'text')
                    else str(phrases)
                )

            elif engine == ProjectSettings.TranscriptionEngine.OPENAI:
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                with open(audio_path, 'rb') as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model='whisper-1', file=audio_file
                    )
                transcription_text = transcript.text

        media_item.transcription = transcription_text.strip()
        media_item.save()

        logger.info(f'Analysis completed for {media_item.id}')

        media_item.status = MediaItem.Status.COMPLETED
        media_item.save()

        try:
            from apps.library.services.rag_service import RAGService

            RAGService().add_to_index(media_item)
        except Exception as e:
            logger.error(f'Failed to index {media_item.id}: {e}')

    except MediaItem.DoesNotExist:
        logger.error(f'MediaItem {media_item_id} not found')
    except Exception as e:
        logger.error(f'Error analyzing {media_item_id}: {e}')
        traceback.print_exc()
        if 'media_item' in locals():
            media_item.status = MediaItem.Status.FAILED
            media_item.error_log = traceback.format_exc()
            media_item.save()
        raise e


@shared_task
def summarize_media(media_item_id):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        media_item.error_log = ''  # Clear error log
        media_item.save()

        logger.info(f'Starting summarization for {media_item.id}')

        project_settings = ProjectSettings.load()
        system_prompt = project_settings.summarization_prompt

        if not media_item.transcription:
            logger.warning(f'No transcription found for {media_item.id}')
            return

        provider = project_settings.llm_provider

        api_key = settings.OPENAI_API_KEY
        base_url = None
        model_name = settings.OPENAI_MODEL

        if provider == ProjectSettings.LLMProvider.DEEPSEEK:
            api_key = settings.DEEPSEEK_API_KEY
            base_url = 'https://api.deepseek.com'
            model_name = settings.DEEPSEEK_MODEL

        llm = ChatOpenAI(
            api_key=api_key, model=model_name, temperature=0, base_url=base_url
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    'You are a professional text summarizer.',
                ),
                ('user', 'Summarize this text:\n\n{text}'),
            ]
        )

        chain = prompt | llm

        response = chain.invoke({'text': media_item.transcription})

        media_item.summary = response.content
        media_item.status = MediaItem.Status.COMPLETED
        media_item.save()

        logger.info(f'Summarization completed for {media_item.id}')

    except MediaItem.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f'Error summarizing {media_item_id}: {e}')
        traceback.print_exc()
        if 'media_item' in locals():
            media_item.status = MediaItem.Status.FAILED
            media_item.error_log = traceback.format_exc()
            media_item.save()
        raise e
