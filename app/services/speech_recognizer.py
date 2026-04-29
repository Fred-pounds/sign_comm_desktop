import os
import json
import vosk

from app.paths import resource_path

class SpeechRecognizer:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = resource_path("models", "vosk-model-small-en-us-0.15")
        
        if not os.path.exists(model_path):
             raise FileNotFoundError(f"Vosk model not found at {model_path}")

        print(f"Loading Vosk model from {model_path}...")
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

    def transcribe_chunk(self, audio_chunk_int16):
        """Processes a chunk of int16 PCM audio directly"""
        if self.recognizer.AcceptWaveform(audio_chunk_int16):
            result = json.loads(self.recognizer.Result())
            return {"text": result.get("text", ""), "is_final": True}
        else:
            partial = json.loads(self.recognizer.PartialResult())
            return {"text": partial.get("partial", ""), "is_final": False}
