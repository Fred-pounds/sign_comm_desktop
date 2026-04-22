import os
import json
import vosk
import numpy as np

class SpeechRecognizer:
    def __init__(self, model_path=None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, "models", "vosk-model-small-en-us-0.15")
        
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
