# audio/tts.py

import os
import subprocess
import wave
from gtts import gTTS
import config

import vlc
import time

import pyttsx3
import threading

class OfflineTextToSpeech:
    def __init__(self, volume=1.0, language="de"):
        self.volume = max(0.0, min(1.0, volume))
        self.language = language

    def speak(self, text: str):
        """
        Offline-TTS mit eSpeak in einem separaten Thread,
        damit das Programm nicht blockiert.
        """
        def run_espeak():
            espeak_volume = int(self.volume * 200)
            os.system(f'espeak -v {self.language} "{text}"')
        print(text)
        t = threading.Thread(target=run_espeak)
        t.start()
        t.join(timeout=5)  # Wenn du willst, dass Python wartet, sonst entfernen

    def play(self, name: str):
        """
        MP3/WAV-Datei abspielen ohne Endlosschleife hängen zu lassen
        """
        if not os.path.exists(name):
            print(f"⚠️ Datei nicht gefunden: {name}")
            return

        p = vlc.MediaPlayer(name)
        p.play()
        # Kurze Pause, damit VLC startet
        time.sleep(0.2)

        # Nicht endlos blockieren: Maximal 30 Sekunden warten
        start = time.time()
        while True:
            state = p.get_state()
            if state in (vlc.State.Ended, vlc.State.Error):
                break
            if time.time() - start > 30:  # Fallback nach 30 Sekunden
                print("⚠️ Wiedergabe Timeout")
                break
            time.sleep(0.1)

    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        print(f"Lautstärke auf {self.volume} gesetzt")
