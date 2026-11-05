"""Command-line translator.

Examples:
    python translate.py "Good morning, how are you?" --to Hindi
    python translate.py "Good morning" --to te --romanize
    python translate.py --file notes.pdf --to Tamil --speak
    python translate.py "नमस्ते" --transliterate Devanagari "Latin (ITRANS)"
"""
from __future__ import annotations

import argparse
import sys

import translator_core as core


def main(argv: list[str] | None = None, backend: core.Translator = core.google_translator) -> int:
    p = argparse.ArgumentParser(description="Translate and transliterate text, files or PDFs.")
    p.add_argument("text", nargs="?", help="Text to translate")
    p.add_argument("--file", help="Read text from a .txt or .pdf file instead")
    p.add_argument("--to", default="English", help=f"Target language: {', '.join(core.LANGUAGES)}")
    p.add_argument("--romanize", action="store_true", help="Also show the translation in Latin letters")
    p.add_argument("--speak", action="store_true", help="Save the translation as translation.mp3")
    p.add_argument("--transliterate", nargs=2, metavar=("FROM", "TO"),
                   help=f"Only change script, no translation. Scripts: {', '.join(core.SCRIPTS)}")
    args = p.parse_args(argv)

    text = core.read_text_file(args.file) if args.file else (args.text or "")
    if not text.strip():
        p.error("give some text or --file")

    try:
        if args.transliterate:
            print(core.transliterate(text, *args.transliterate))
            return 0
        result = core.translate(text, args.to, backend=backend)
        print(result)
        if args.romanize:
            roman = core.romanize(result, args.to)
            if roman:
                print(roman)
        if args.speak:
            print(f"Saved {core.speak(result, args.to)}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # network or service problems
        print(f"Could not reach the translation service. Check your internet connection. ({type(e).__name__})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
