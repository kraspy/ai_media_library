import gc

import torch
import whisperx
from celery import shared_task
from django.conf import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .models import MediaItem


@shared_task
def transcribe_media(media_item_id):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        media_item.status = MediaItem.Status.PROCESSING
        media_item.save()

        device = settings.WHISPER_DEVICE
        batch_size = 16
        compute_type = settings.WHISPER_COMPUTE_TYPE

        model = whisperx.load_model(
            settings.WHISPER_MODEL,
            device,
            compute_type=compute_type,
        )

        audio = whisperx.load_audio(media_item.file.path)
        result = model.transcribe(audio, batch_size=batch_size)

        del model
        gc.collect()
        if device == 'cuda':
            torch.cuda.empty_cache()

        transcription_text = ''
        for segment in result['segments']:
            transcription_text += segment['text'] + '\n'

        media_item.transcription = transcription_text.strip()
        media_item.save()

        # SUMMARIZATION
        summarize_media.delay(media_item.id)

    except MediaItem.DoesNotExist:
        pass
    except Exception as e:
        if 'media_item' in locals():
            media_item.status = MediaItem.Status.FAILED
            media_item.save()
        raise e


@shared_task
def summarize_media(media_item_id):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)

        if not media_item.transcription:
            return

        llm = ChatOpenAI(
            api_key=settings.OPEANI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    'You are a professiona text summarizer.',
                ),
                ('user', 'Summarize this text:\n\n{text}'),
            ]
        )

        chain = prompt | llm

        response = chain.invoke({'text': media_item.transcription})

        media_item.summary = response.content
        media_item.status = MediaItem.Status.COMPLETED
        media_item.save()

    except MediaItem.DoesNotExist:
        pass
    except Exception as e:
        if 'media_item' in locals():
            media_item.status = MediaItem.Status.FAILED
            media_item.save()
        raise e
