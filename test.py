import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

# ====== Einstellungen ======
MODEL_PATH = "models/vosk-model-small-de-0.15"
SAMPLE_RATE = 16000
DEVICE = None        # None = Standard-Mikrofon
BLOCKSIZE = 8000

# ===========================

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def main():
    print("🔊 Lade Sprachmodell...")
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetWords(True)

    print("🎤 Starte kontinuierliche Spracherkennung (Strg+C zum Beenden)")

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCKSIZE,
        device=DEVICE,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print("➡️", text)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Beendet")
