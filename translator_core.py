"""Translation, transliteration, file reading and speech output, independent of any UI.

The Tkinter app (app.py) and the command-line tool (translate.py) both call these
functions, and the tests exercise them directly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate as _transliterate

# Languages offered for translation: display name -> ISO 639-1 code
LANGUAGES: dict[str, str] = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Punjabi": "pa",
}

# Scripts offered for transliteration: display name -> indic_transliteration scheme.
# "Latin (ITRANS)" is the romanized form, e.g. "namaste".
SCRIPTS: dict[str, str] = {
    "Latin (ITRANS)": sanscript.ITRANS,
    "Devanagari": sanscript.DEVANAGARI,  # Hindi, Marathi, Sanskrit, Nepali
    "Telugu": sanscript.TELUGU,
    "Tamil": sanscript.TAMIL,
    "Kannada": sanscript.KANNADA,
    "Malayalam": sanscript.MALAYALAM,
    "Bengali": sanscript.BENGALI,      # Bengali, Assamese
    "Gujarati": sanscript.GUJARATI,
    "Gurmukhi": sanscript.GURMUKHI,    # Punjabi
    "Oriya": sanscript.ORIYA,
}

# Script each translation target is written in, so a translation can be romanized directly.
LANGUAGE_SCRIPT: dict[str, str] = {
    "hi": "Devanagari", "mr": "Devanagari", "te": "Telugu", "ta": "Tamil", "kn": "Kannada",
    "ml": "Malayalam", "bn": "Bengali", "gu": "Gujarati", "pa": "Gurmukhi",
}


class Translator(Protocol):
    def __call__(self, text: str, source: str, target: str) -> str: ...


def google_translator(text: str, source: str, target: str) -> str:
    """Default backend: Google Translate through the maintained deep-translator package."""
    from deep_translator import GoogleTranslator

    return GoogleTranslator(source=source, target=target).translate(text)


def language_code(name_or_code: str) -> str:
    """Accept 'Hindi', 'hindi' or 'hi' and return 'hi'."""
    value = name_or_code.strip()
    if value in LANGUAGES.values():
        return value
    for name, code in LANGUAGES.items():
        if name.lower() == value.lower():
            return code
    raise ValueError(f"Unsupported language: {name_or_code!r}. Choose from {', '.join(LANGUAGES)}")


def translate(text: str, target: str, source: str = "auto", backend: Translator = google_translator) -> str:
    text = text.strip()
    if not text:
        raise ValueError("Enter some text to translate")
    return backend(text, source, language_code(target))


def transliterate(text: str, from_script: str, to_script: str) -> str:
    """Convert text between scripts without changing the language, e.g. Devanagari to Latin."""
    for s in (from_script, to_script):
        if s not in SCRIPTS:
            raise ValueError(f"Unsupported script: {s!r}. Choose from {', '.join(SCRIPTS)}")
    return _transliterate(text, SCRIPTS[from_script], SCRIPTS[to_script])


def romanize(text: str, language: str) -> str | None:
    """Romanize a translation (e.g. Hindi output) so it can be read in Latin letters."""
    script = LANGUAGE_SCRIPT.get(language_code(language))
    return transliterate(text, script, "Latin (ITRANS)") if script else None


def read_text_file(path: str | Path) -> str:
    """Read a .txt or .pdf file and return its text."""
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        return "\n".join((page.extract_text() or "") for page in PdfReader(path).pages).strip()
    return path.read_text(encoding="utf-8").strip()


def speak(text: str, language: str, out_file: str | Path = "translation.mp3",
          tts: Callable[..., object] | None = None) -> Path:
    """Save spoken audio of the text with Google Text-to-Speech and return the file path."""
    if tts is None:
        from gtts import gTTS as tts
    out = Path(out_file)
    tts(text=text, lang=language_code(language), slow=False).save(str(out))
    return out
