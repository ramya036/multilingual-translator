from pathlib import Path

import pytest

import translate as cli
import translator_core as core


def fake_backend(text, source, target):
    """Stands in for Google Translate so tests run offline."""
    phrasebook = {("Hello", "hi"): "नमस्ते", ("Hello", "te"): "నమస్తే"}
    return phrasebook.get((text, target), f"[{target}] {text}")


def test_language_code_accepts_names_and_codes():
    assert core.language_code("Hindi") == "hi"
    assert core.language_code("telugu") == "te"
    assert core.language_code("ta") == "ta"
    with pytest.raises(ValueError):
        core.language_code("Klingon")


def test_translate_uses_backend_and_strips_input():
    assert core.translate("  Hello \n", "Hindi", backend=fake_backend) == "नमस्ते"


def test_translate_rejects_empty_text():
    with pytest.raises(ValueError):
        core.translate("   ", "Hindi", backend=fake_backend)


@pytest.mark.parametrize("text, src, dst, expected", [
    ("नमस्ते", "Devanagari", "Latin (ITRANS)", "namaste"),
    ("namaste", "Latin (ITRANS)", "Telugu", "నమస్తే"),
    ("नमस्ते", "Devanagari", "Telugu", "నమస్తే"),
    ("నమస్కారం", "Telugu", "Latin (ITRANS)", "namaskAraM"),
])
def test_transliterate_between_scripts(text, src, dst, expected):
    assert core.transliterate(text, src, dst) == expected


def test_transliterate_rejects_unknown_script():
    with pytest.raises(ValueError):
        core.transliterate("abc", "Klingon", "Telugu")


def test_romanize_translation():
    assert core.romanize("नमस्ते", "Hindi") == "namaste"
    assert core.romanize("Hello", "English") is None


def test_every_language_with_a_script_maps_to_a_known_script():
    for code, script in core.LANGUAGE_SCRIPT.items():
        assert code in core.LANGUAGES.values() and script in core.SCRIPTS


def test_read_text_file(tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("Good morning\n", encoding="utf-8")
    assert core.read_text_file(f) == "Good morning"


def test_read_pdf_file(tmp_path):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="Good morning from a PDF")
    path = tmp_path / "note.pdf"
    pdf.output(str(path))
    assert "Good morning from a PDF" in core.read_text_file(path)


def test_speak_saves_audio_with_language_code(tmp_path):
    calls = {}

    class FakeTTS:
        def __init__(self, text, lang, slow):
            calls.update(text=text, lang=lang)

        def save(self, path):
            Path(path).write_bytes(b"ID3")

    out = core.speak("नमस्ते", "Hindi", tmp_path / "a.mp3", tts=FakeTTS)
    assert out.exists() and calls == {"text": "नमस्ते", "lang": "hi"}


def test_cli_translate_and_romanize(capsys):
    assert cli.main(["Hello", "--to", "Hindi", "--romanize"], backend=fake_backend) == 0
    assert capsys.readouterr().out.split() == ["नमस्ते", "namaste"]


def test_cli_transliterate_only(capsys):
    assert cli.main(["नमस्ते", "--transliterate", "Devanagari", "Telugu"]) == 0
    assert capsys.readouterr().out.strip() == "నమస్తే"


def test_cli_reports_bad_language(capsys):
    assert cli.main(["Hello", "--to", "Klingon"], backend=fake_backend) == 2
    assert "Unsupported language" in capsys.readouterr().err
