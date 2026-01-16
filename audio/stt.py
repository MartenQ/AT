#stt.py

import os
import json
import subprocess
import time

os.environ["VOSK_LOG_LEVEL"] = "1"  # 0 = keine Logs, 1 = Fehler, 2 = Warnungen, 3 = Info
from vosk import Model, KaldiRecognizer

class OfflineSpeechToText:
    def __init__(
        self,
        wake_words=None,  # jetzt eine Liste von Wake-Wörtern
        model_path="models/vosk-model-small-de-0.15",
        device="plughw:2,0",
        sample_rate=16000,
        channels=1,
        chunk_size=4000,
        max_record_seconds=5
    ):
        # Standard-Wake-Wortliste, falls None übergeben
        self.wake_words = [w.lower() for w in wake_words] if wake_words else ["roboter"]
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.max_record_seconds = max_record_seconds

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modell nicht gefunden: {model_path}")

        self.model = Model(model_path)

    def listen_once(self):
        """
        Hört kontinuierlich auf Wake-Words und danach auf ein Kommando.
        Rückgabe: (detected_wake_word, command_text)
        """
        recognizer = KaldiRecognizer(self.model, self.sample_rate)

        process = subprocess.Popen(
            [
                "arecord",
                "-D", self.device,
                "-f", "S16_LE",
                "-r", str(self.sample_rate),
                "-c", str(self.channels)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        detected_wake_word = None
        collected_text = []
        silence_chunks = 0
        max_silence_chunks = int(self.sample_rate / self.chunk_size * 1.5)  # ~1.5s Stille

        start_time = time.time()

        try:
            while True:
                data = process.stdout.read(self.chunk_size)
                if not data:
                    break

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").lower()

                    if text:
                        print("🎧", text)
                        collected_text.append(text)

                        # Wake-Word-Erkennung
                        if not detected_wake_word:
                            for word in self.wake_words:
                                if word in text:
                                    detected_wake_word = word
                                    print(f"🟢 Wake-Word erkannt: {word}")

                                    # Wake-Word entfernen, Kommando behalten
                                    cleaned = text.replace(word, "").strip()
                                    collected_text = []
                                    if cleaned:
                                        collected_text.append(cleaned)
                                    # Startzeit für Kommandoaufnahme setzen
                                    start_time = time.time()
                                    break
                        else:
                            silence_chunks = 0
                else:
                    if detected_wake_word:
                        silence_chunks += 1
                        if silence_chunks > max_silence_chunks:
                            break

                # Maximale Aufnahmezeit prüfen
                if detected_wake_word and (time.time() - start_time) > self.max_record_seconds:
                    print("⏱ Maximale Aufnahmezeit erreicht")
                    break

        finally:
            process.terminate()

        command_text = " ".join(collected_text).strip() if detected_wake_word else None
        return detected_wake_word, command_text
