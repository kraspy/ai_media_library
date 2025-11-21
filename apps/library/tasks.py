import time

from celery import shared_task

from .models import MediaItem


@shared_task
def transcribe_media(media_item_id):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        media_item.status = MediaItem.Status.PROCESSING
        media_item.save()

        time.sleep(5)

        transcription = (
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
            'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
            'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. '
            'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. '
            'Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
        )

        media_item.transcription = transcription
        media_item.status = MediaItem.Status.COMPLETED
        media_item.save()

    except MediaItem.DoesNotExist:
        pass
    except Exception as e:
        if 'media_item' in locals():
            media_item.status = MediaItem.Status.FAILED
            media_item.save()
        raise e
