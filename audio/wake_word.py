#wake_word.py

from audio.stt import OfflineSpeechToText
import time

class WakeWordListener:
    def __init__(self, stt, wake_word="roboter"):
        self.stt = stt
        self.wake_word = wake_word.lower()

    def listen_for_wake_word(self):
    print("👂 Warte auf Wake-Word...")
    recognizer = KaldiRecognizer(self.model, self.sample_rate)

    import pyaudio
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                     channels=self.channels,
                     rate=self.sample_rate,
                     input=True,
                     frames_per_buffer=self.chunk_size)

    while True:
        data = stream.read(self.chunk_size, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            res = json.loads(recognizer.Result())
            text = res.get("text", "").lower()
            if any(word in text for word in self.wake_words):
                print("🚀 Wake-Word erkannt")
                stream.stop_stream()
                stream.close()
                pa.terminate()
                return text
