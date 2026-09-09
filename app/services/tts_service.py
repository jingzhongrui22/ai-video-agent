"""Single-text speech synthesis using edge-tts."""

from pathlib import Path
from uuid import uuid4

import edge_tts


AUDIO_DIR = Path(__file__).resolve().parents[2] / "storage" / "audio"


async def synthesize_text(
    text: str,
    voice: str = "zh-CN-YunxiNeural",
) -> str:
    """Save speech as a UUID-named MP3 and return its absolute path."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = AUDIO_DIR / f"{uuid4()}.mp3"
    try:
        await edge_tts.Communicate(text=text, voice=voice).save(str(audio_path))
    except BaseException:
        # Remove incomplete output, including when synthesis is cancelled.
        audio_path.unlink(missing_ok=True)
        raise
    return str(audio_path)
