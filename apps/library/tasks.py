import gc

import torch
import whisperx
from celery import shared_task
from django.conf import settings

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
        media_item.status = MediaItem.Status.COMPLETED
        media_item.save()

    except MediaItem.DoesNotExist:
        pass
    except Exception as e:
        if 'media_item' in locals():
            media_item.status = MediaItem.Status.FAILED
            media_item.save()
        raise e
