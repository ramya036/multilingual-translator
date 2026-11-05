# Multilingual Translator & Transliterator

A desktop app that translates and transliterates between languages. Input can be **typed text, a PDF or text file, or live speech**, and the result comes back as **text and spoken audio**. It's especially useful for Indian languages, where transliteration (for example, Devanagari ↔ Kannada script) matters as much as translation.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-blue)

![App screenshot](https://github.com/vyshnavi1402/MultiLingual-Translator-and-Transliterator/assets/108367765/91486722-0268-4dd6-9523-0a8868df5269)

## Features

- **Translate** between dozens of languages with Google Translate (`googletrans`)
- **Transliterate** Indian scripts with `indic_transliteration`
- **Three input modes:** type text, browse for a PDF or text file (`PyPDF2`), or speak into the microphone (`SpeechRecognition`)
- **Spoken output** with Google Text-to-Speech (`gTTS`)
- Simple Tkinter interface

## Run it

```bash
pip install -r requirements.txt
python code.py
```

PyAudio may need extra system packages: `brew install portaudio` on macOS, or `sudo apt install portaudio19-dev` on Ubuntu.

## Tech

Python · Tkinter · googletrans · gTTS · SpeechRecognition · PyAudio · PyPDF2 · indic-transliteration · Pillow
