"""Desktop app: type, open a .txt/.pdf file, or speak; then translate, romanize and listen."""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import translator_core as core

PAD = {"padx": 10, "pady": 6}


def play(path: str) -> None:
    """Open the audio file with the system's default player."""
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["afplay", path])
    else:
        subprocess.Popen(["xdg-open", path])


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Multilingual Translator & Transliterator")
        self.geometry("980x640")
        self.minsize(760, 520)
        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure(1, weight=1)

        # Input side
        top_in = ttk.Frame(self)
        top_in.grid(row=0, column=0, sticky="ew", **PAD)
        ttk.Label(top_in, text="Your text", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(top_in, text="Open file", command=self.open_file).pack(side="right")
        ttk.Button(top_in, text="Speak", command=self.listen).pack(side="right", padx=6)
        self.source = tk.Text(self, wrap="word", font=("Segoe UI", 12), height=10)
        self.source.grid(row=1, column=0, sticky="nsew", **PAD)

        # Output side
        top_out = ttk.Frame(self)
        top_out.grid(row=0, column=1, sticky="ew", **PAD)
        ttk.Label(top_out, text="Translate to", font=("Segoe UI", 12, "bold")).pack(side="left")
        self.target = ttk.Combobox(top_out, values=list(core.LANGUAGES), state="readonly", width=14)
        self.target.set("Hindi")
        self.target.pack(side="left", padx=8)
        self.output = tk.Text(self, wrap="word", font=("Segoe UI", 12), height=10)
        self.output.grid(row=1, column=1, sticky="nsew", **PAD)

        actions = ttk.Frame(self)
        actions.grid(row=2, column=0, columnspan=2, **PAD)
        ttk.Button(actions, text="Translate", command=self.translate).pack(side="left", padx=4)
        ttk.Button(actions, text="Listen", command=self.listen_output).pack(side="left", padx=4)
        ttk.Button(actions, text="Clear", command=self.clear).pack(side="left", padx=4)

        # Transliteration
        tl = ttk.LabelFrame(self, text="Transliterate the translation (change script only)")
        tl.grid(row=3, column=0, columnspan=2, sticky="ew", **PAD)
        self.from_script = ttk.Combobox(tl, values=list(core.SCRIPTS), state="readonly", width=16)
        self.to_script = ttk.Combobox(tl, values=list(core.SCRIPTS), state="readonly", width=16)
        self.from_script.set("Devanagari")
        self.to_script.set("Latin (ITRANS)")
        self.from_script.pack(side="left", padx=6, pady=6)
        ttk.Label(tl, text="to").pack(side="left")
        self.to_script.pack(side="left", padx=6)
        ttk.Button(tl, text="Transliterate", command=self.transliterate).pack(side="left", padx=6)
        self.translit = ttk.Label(tl, text="", font=("Segoe UI", 12), wraplength=520)
        self.translit.pack(side="left", padx=10)

        self.status = ttk.Label(self, text="Type, open a file or press Speak, then choose a language.")
        self.status.grid(row=4, column=0, columnspan=2, sticky="w", **PAD)

    # --- actions ---------------------------------------------------------
    def open_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Text or PDF", "*.txt *.pdf"), ("All files", "*.*")])
        if path:
            self.source.delete("1.0", "end")
            self.source.insert("1.0", core.read_text_file(path))
            self.status.config(text=f"Loaded {os.path.basename(path)}")

    def listen(self) -> None:
        def work() -> None:
            import speech_recognition as sr

            r = sr.Recognizer()
            try:
                with sr.Microphone() as mic:
                    r.adjust_for_ambient_noise(mic)
                    self.status.config(text="Listening...")
                    audio = r.listen(mic, phrase_time_limit=10)
                text = r.recognize_google(audio)
                self.after(0, lambda: (self.source.insert("end", text), self.status.config(text="Got it.")))
            except Exception as e:  # microphone missing, nothing heard, no network
                self.after(0, lambda: self.status.config(text=f"Could not hear that: {e}"))

        threading.Thread(target=work, daemon=True).start()

    def translate(self) -> None:
        text = self.source.get("1.0", "end")
        try:
            result = core.translate(text, self.target.get())
        except ValueError as e:
            messagebox.showinfo("Nothing to translate", str(e))
            return
        except Exception:
            messagebox.showerror("Translation failed", "Could not reach Google Translate. Check your internet connection and try again.")
            return
        self.output.delete("1.0", "end")
        self.output.insert("1.0", result)
        script = core.LANGUAGE_SCRIPT.get(core.language_code(self.target.get()))
        if script:
            self.from_script.set(script)
        self.status.config(text=f"Translated to {self.target.get()}.")

    def listen_output(self) -> None:
        text = self.output.get("1.0", "end").strip()
        if text:
            play(str(core.speak(text, self.target.get())))

    def transliterate(self) -> None:
        text = self.output.get("1.0", "end").strip() or self.source.get("1.0", "end").strip()
        self.translit.config(text=core.transliterate(text, self.from_script.get(), self.to_script.get()))

    def clear(self) -> None:
        self.source.delete("1.0", "end")
        self.output.delete("1.0", "end")
        self.translit.config(text="")


if __name__ == "__main__":
    App().mainloop()
