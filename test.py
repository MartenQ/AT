import subprocess
import json
import wave
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-model-small-de-0.15"
DEVICE = "plughw:2,0"
RATE = 16000

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, RATE)

print("🎤 Lausche kontinuierlich... (Strg+C zum Beenden)")

process = subprocess.Popen(
    [
        "arecord",
        "-D", DEVICE,
        "-f", "S16_LE",
        "-r", str(RATE),
        "-c", "1",
        "-t", "raw"
    ],
    stdout=subprocess.PIPE
)

try:
    while True:
        data = process.stdout.read(4000)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print("➡️", text)

except KeyboardInterrupt:
    print("\n🛑 Stop")
    process.terminate()