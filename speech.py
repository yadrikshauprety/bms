import vosk
import sounddevice as sd
import queue
import sys

# Map language codes to model folders
model_paths = {
    "en": "models/vosk-model-small-en-0.15",
    "hi": "models/vosk-model-small-hi-0.4"
}

def speech_to_text(lang="en", duration=5):
    model_path = model_paths.get(lang, model_paths["en"])
    try:
        model = vosk.Model(model_path)
    except Exception as e:
        raise Exception(f"Failed to load Vosk model: {e}")

    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, 16000)
        result_text = ""
        import time
        start_time = time.time()
        while time.time() - start_time < duration:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = rec.Result()
                import json
                result_text += json.loads(result).get("text", "") + " "
        return result_text.strip()
