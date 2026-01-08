# audio/player.py

import os
import subprocess
from gtts import gTTS
import config


class AudioPlayer:
    """
    Spielt Audio ab:
    - Wenn WAV vorhanden: direkt abspielen
    - Wenn nur MP3 vorhanden: in WAV umwandeln (mit optionaler Lautstärke) und abspielen
    - Kann Text direkt zu Sprache umwandeln, speichern und abspielen
    """

    def __init__(self, volume=config.TTS_VOLUME):
        self.volume = volume


    def play(self, file_path: str):
        """
        Spielt eine WAV- oder MP3-Datei ab. 
        Falls MP3, wird diese in WAV umgewandelt und dann abgespielt.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")

        # Pfad für WAV-Datei
        if file_path.lower().endswith(".wav"):
            wav_path = file_path
        elif file_path.lower().endswith(".mp3"):
            wav_path = file_path.rsplit(".", 1)[0] + "_temp.wav"
            self._mp3_to_wav(file_path, wav_path)
        else:
            raise ValueError("Nur WAV oder MP3 Dateien werden unterstützt.")

        # Abspielen
        subprocess.run(
            ["aplay", wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Temporäre WAV löschen, falls von MP3 konvertiert
        if file_path.lower().endswith(".mp3"):
            os.remove(wav_path)


    def _mp3_to_wav(self, mp3_path: str, wav_path: str):
        """
        Konvertiert MP3 in WAV mit optionaler Lautstärkeanpassung.
        """
        os.system(
            f'ffmpeg -y -i "{mp3_path}" '
            f'-filter:a "volume={self.volume}" '
            f'"{wav_path}" > /dev/null 2>&1'
        )

    def set_volume(self, volume: float):
        """
        Setzt die Lautstärke (0.0 bis 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
