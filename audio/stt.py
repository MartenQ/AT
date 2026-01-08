import os
import json
import subprocess
import tempfile
import wave
os.environ["VOSK_LOG_LEVEL"] = "1"  # 0 = keine Logs, 1 = Fehler, 2 = Warnungen, 3 = Info
from vosk import Model, KaldiRecognizer
from config.config import max_record_seconds

class OfflineSpeechToText:
    def __init__(
        self,
        wake_words=None,  # jetzt eine Liste von Wake-Wörtern
        model_path="models/vosk-model-small-de-0.15",
        device="plughw:2,0",
        sample_rate=16000,
        channels=1,
        chunk_size=4000,
        max_record_seconds=max_record_seconds,
        SetLogLevel=-1
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
        Hört einmal auf Wake-Words + Befehl in einem Durchgang.
        Gibt zurück: (detected_wake_word: str | None, command_text: str | None)
        """
        recognizer = KaldiRecognizer(self.model, self.sample_rate)

        # Temporäre WAV-Datei
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name

        # Aufnahme
        subprocess.run(
            [
                "arecord",
                "-D", self.device,
                "-c", str(self.channels),
                "-r", str(self.sample_rate),
                "-f", "S16_LE",
                "-d", str(self.max_record_seconds),
                wav_path
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Erkennen
        wf = wave.open(wav_path, "rb")
        result_text = ""
        detected_wake_word = None

        while True:
            data = wf.readframes(self.chunk_size)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                res = json.loads(recognizer.Result())
                text = res.get("text", "").lower()
                print(text)
                if text:
                    result_text += " " + text
                    for word in self.wake_words:
                        if word in text:
                            detected_wake_word = word

        # Letztes Ergebnis
        res = json.loads(recognizer.FinalResult())
        text = res.get("text", "").lower()
        if text:
            result_text += " " + text
            for word in self.wake_words:
                if word in text:
                    detected_wake_word = word

        wf.close()
        os.remove(wav_path)

        command_text = result_text.replace(detected_wake_word, "").strip() if detected_wake_word else None
        return detected_wake_word, command_text
