import numpy as np
import ai_edge_litert.interpreter as tflite

from app.paths import resource_path

class GestureRecognizer:
    def __init__(self, model_path=None, label_path=None, threshold=0.8):
        self.threshold = threshold
        self.sequence_length = 30
        self.sequence_buffer = []
        
        if model_path is None:
            model_path = resource_path("models", "lstm_model.tflite")
        if label_path is None:
            label_path = resource_path("models", "labels.txt")

        self.labels = []
        try:
            with open(label_path, "r") as f:
                self.labels = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(f"Warning: {label_path} not found.")
            
        try:
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
        except Exception as e:
            print(f"Error loading LSTM model: {e}")
            raise

    def process_landmarks(self, landmarks):
        lm_np = np.array(landmarks)
        wrist = lm_np[:3]
        relative_lm = lm_np - np.tile(wrist, 21)
        
        self.sequence_buffer.append(relative_lm)
        if len(self.sequence_buffer) > self.sequence_length:
            self.sequence_buffer.pop(0)
            
        padded_buffer = list(self.sequence_buffer)
        if len(padded_buffer) < self.sequence_length:
            padded_buffer.extend([relative_lm] * (self.sequence_length - len(padded_buffer)))
            
        return self._predict(padded_buffer)

    def _predict(self, sequence):
        input_data = np.array([sequence], dtype=np.float32)
        try:
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            prediction = np.squeeze(output_data)
            max_index = np.argmax(prediction)
            confidence = prediction[max_index]
            
            if confidence > self.threshold:
                return {
                    "text": self.labels[max_index] if self.labels else str(max_index),
                    "confidence": float(confidence)
                }
        except Exception as e:
            print(f"Inference error: {e}")
        return None

    def clear(self):
        self.sequence_buffer = []
