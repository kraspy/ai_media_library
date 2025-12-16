import logging
import subprocess
from pathlib import Path

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


def cut_audio_from_video(video_path: Path) -> Path:
    """
    Extracts audio from video using ffmpeg and converts to wav using faad (if needed) or just ffmpeg.
    The user requested specific ffmpeg + faad pipeline.
    """
    audio_dir = video_path.parent
    m4a_path = audio_dir / video_path.with_suffix('.m4a').name
    wav_path = audio_dir / video_path.with_suffix('.wav').name

    logger.info(f'Extracting audio from {video_path} to {m4a_path}')

    subprocess.run(
        [
            'ffmpeg',
            '-y',
            '-i',
            str(video_path),
            '-vn',
            '-c:a',
            'copy',
            str(m4a_path),
        ],
        check=True,
        capture_output=True,
    )

    logger.info(f'Converting {m4a_path} to {wav_path} using ffmpeg')

    subprocess.run(
        [
            'ffmpeg',
            '-y',
            '-i',
            str(m4a_path),
            '-ac',
            '1',
            '-ar',
            '16000',
            str(wav_path),
        ],
        check=True,
        capture_output=True,
    )

    if m4a_path.exists():
        m4a_path.unlink()

    return wav_path


def perform_ocr(image_path: Path) -> str:
    """
    Extracts text from image using pytesseract.
    """
    logger.info(f'Performing OCR on {image_path}')
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='eng+rus')
        return text
    except Exception as e:
        logger.error(f'OCR failed: {e}')
        raise e
