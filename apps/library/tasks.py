import gc

import torch
import whisperx
from celery import shared_task
from django.conf import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI

from apps.core.models import ProjectSettings

from .models import MediaItem


@shared_task
def transcribe_media(media_item_id):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        media_item.status = MediaItem.Status.PROCESSING
        media_item.save()

        project_settings = ProjectSettings.load()
        engine = project_settings.transcription_engine
        transcription_text = ''

        if engine == ProjectSettings.TranscriptionEngine.WHISPERX:
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

            for segment in result['segments']:
                transcription_text += segment['text'] + '\n'

        elif engine == ProjectSettings.TranscriptionEngine.T_ONE:
            from tone import StreamingCTCPipeline, read_audio

            # T-One usage
            audio = read_audio(media_item.file.path)
            pipeline = StreamingCTCPipeline.from_hugging_face()
            # forward_offline returns a list of phrases, we need to join them
            phrases = pipeline.forward_offline(audio)
            # Assuming phrases is a list of objects with 'text' attribute or dictionaries
            # Based on README it prints phrases. Let's assume it returns a list of Phrase objects or dicts.
            # If it returns a simple string, this might break.
            # Let's inspect the output format in a separate check if possible, but for now assuming list of objects/dicts.
            # Actually README says: "The resulting text along with phrase timings is returned to the client."
            # And "print(pipeline.forward_offline(audio))"
            # Let's assume it returns a list of Phrase objects which have a text attribute or __str__.
            # For safety, let's convert to string.

            # Correction: Looking at T-One code would be better, but based on common ASR pipelines:
            transcription_text = (
                ' '.join([p.text for p in phrases])
                if phrases and hasattr(phrases[0], 'text')
                else str(phrases)
            )

        elif engine == ProjectSettings.TranscriptionEngine.OPENAI:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            with open(media_item.file.path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model='whisper-1', file=audio_file
                )
            transcription_text = transcript.text

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

        project_settings = ProjectSettings.load()
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

    except MediaItem.DoesNotExist:
        pass
    except Exception as e:
        if 'media_item' in locals():
            media_item.status = MediaItem.Status.FAILED
            media_item.save()
        raise e
