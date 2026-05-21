"""Translation & Text-to-Speech Service — deep-translator + gTTS (both free).

Translates medical text to Hindi/Bengali and generates downloadable audio MP3.
"""
import os
import uuid
from deep_translator import GoogleTranslator
from gtts import gTTS
from typing import Optional


SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "en": "English",
}

AUDIO_DIR = "audio_files"


async def translate_text(text: str, target_lang: str = "hi", source_lang: str = "en") -> str:
    """Translate text using deep-translator (free, uses Google Translate)."""
    if target_lang == source_lang:
        return text

    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)

        if len(text) > 4500:
            chunks = _chunk_text(text, 4500)
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            return " ".join(translated_chunks)

        return translator.translate(text)
    except Exception as e:
        return f"Translation error: {str(e)}"


async def text_to_audio(text: str, lang: str = "hi", filename: Optional[str] = None) -> str:
    """Convert text to speech audio MP3 using gTTS (free).

    Returns the file path of the generated MP3.
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)

    if not filename:
        filename = f"{uuid.uuid4().hex}.mp3"

    filepath = os.path.join(AUDIO_DIR, filename)

    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filepath)
        return filepath
    except Exception as e:
        raise Exception(f"TTS generation failed: {str(e)}")


async def translate_and_speak(
    text: str,
    target_lang: str = "hi",
    source_lang: str = "en"
) -> dict:
    """Translate text and generate audio — combined workflow for discharge summaries.

    Returns both translated text and audio file path.
    """
    translated = await translate_text(text, target_lang, source_lang)

    if translated.startswith("Translation error"):
        return {"translated_text": translated, "audio_path": None, "error": translated}

    try:
        audio_path = await text_to_audio(translated, target_lang)
        audio_filename = os.path.basename(audio_path)

        return {
            "original_text": text,
            "translated_text": translated,
            "target_language": SUPPORTED_LANGUAGES.get(target_lang, target_lang),
            "audio_path": f"/audio/{audio_filename}",
            "audio_filename": audio_filename,
        }
    except Exception as e:
        return {
            "original_text": text,
            "translated_text": translated,
            "target_language": SUPPORTED_LANGUAGES.get(target_lang, target_lang),
            "audio_path": None,
            "error": str(e),
        }


def get_supported_languages() -> dict:
    """Return the list of supported languages."""
    return SUPPORTED_LANGUAGES


def _chunk_text(text: str, max_length: int) -> list:
    """Split text into chunks at sentence boundaries."""
    sentences = text.replace(". ", ".\n").split("\n")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + " "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
