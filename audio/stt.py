import os
import json
import wave
import time
import threading
import tempfile
import subprocess
from vosk import Model, KaldiRecognizer
from config.config import max_record_seconds

class OfflineSpeechToText:
    def __init__(
        self,
        wake_words=None,  # Liste von Wake-Wörtern
        model_path="models/vosk-model-small-de-0.15",
        device="plughw:2,0",
        sample_rate=16000,
        channels=1,
        chunk_size=4000,
        max_record_seconds=max_record_seconds,
        SetLogLevel=-1
    ):
        self.wake_words = [w.lower() for w in wake_words] if wake_words else ["roboter"]
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.max_record_seconds = max_record_seconds

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modell nicht gefunden: {model_path}")

        self.model = Model(model_path)

    def listen_for_wake_word_and_command(self, wake_window=5, overlap=1):
        """
        Überlappende Fenster für Wake-Word-Erkennung.
        wake_window: Länge des Wake-Word-Fensters (≥5 Sekunden)
        overlap: Wie oft ein neues Fenster gestartet wird (z.B. jede Sekunde)
        """

        detected_wake_word = None
        command_text = None

        # Thread für parallele Befehlsaufnahme
        def record_long_command(temp_file_path, duration=15):
            subprocess.run([
                "arecord",
                "-D", self.device,
                "-c", str(self.channels),
                "-r", str(self.sample_rate),
                "-f", "S16_LE",
                "-d", str(duration),
                temp_file_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("👂 Warte auf Wake-Word...")

        start_time = time.time()
        while True:
            # Aufnahme eines Fensters
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                wav_path = f.name

            subprocess.run([
                "arecord",
                "-D", self.device,
                "-c", str(self.channels),
                "-r", str(self.sample_rate),
                "-f", "S16_LE",
                "-d", str(wake_window),
                wav_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Vosk Recognizer
            recognizer = KaldiRecognizer(self.model, self.sample_rate)
            wf = wave.open(wav_path, "rb")
            result_text = ""
            while True:
                data = wf.readframes(self.chunk_size)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    res = json.loads(recognizer.Result())
                    text = res.get("text", "").lower()
                    result_text += " " + text

            # Letztes Ergebnis
            res = json.loads(recognizer.FinalResult())
            text = res.get("text", "").lower()
            result_text += " " + text

            # Prüfen auf Wake-Word
            for word in self.wake_words:
                if word in result_text:
                    detected_wake_word = word
                    break

            wf.close()
            os.remove(wav_path)

            if detected_wake_word:
                print("🚀 Wake-Word erkannt")
                
                # Sofort langen Befehl aufnehmen
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as cmd_f:
                    cmd_path = cmd_f.name
                t = threading.Thread(target=record_long_command, args=(cmd_path, 15))
                t.start()
                t.join()

                # Befehl transkribieren
                wf = wave.open(cmd_path, "rb")
                recognizer = KaldiRecognizer(self.model, self.sample_rate)
                command_text = ""
                while True:
                    data = wf.readframes(self.chunk_size)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        res = json.loads(recognizer.Result())
                        command_text += " " + res.get("text", "").lower()
                res = json.loads(recognizer.FinalResult())
                command_text += " " + res.get("text", "").lower()
                wf.close()
                os.remove(cmd_path)

                # Wake-Word aus Befehl entfernen
                command_text = command_text.replace(detected_wake_word, "").strip()
                return detected_wake_word, command_text

            # Überlappung realisieren: kurze Pause vor nächstem Fenster
            time.sleep(overlap)
