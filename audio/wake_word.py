from audio.stt import OfflineSpeechToText
import time

class WakeWordListener:
    def __init__(self, stt, wake_word="roboter"):
        self.stt = stt
        self.wake_word = wake_word.lower()

    def listen_for_wake_word(self):
    print("👂 Warte auf Wake-Word...")
    while True:
        text = self.stt.listen_once(seconds=1)
        if not text:
            continue
        print("Gehört:", text)
        if any(word in text.lower() for word in self.wake_words):
            print("🚀 Wake-Word erkannt")
            return