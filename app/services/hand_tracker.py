import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

class HandTracker:
    def __init__(self, max_hands=1, detection_con=0.5, track_con=0.5, model_path=None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, "models", "hand_landmarker.task")
            
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_hand_presence_confidence=track_con
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.results = None

    def find_hands(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        self.results = self.detector.detect(mp_image)
        return self.results
        
    def draw_hands(self, img):
        if self.results and self.results.hand_landmarks:
            for hand_landmarks in self.results.hand_landmarks:
                for idx, lm in enumerate(hand_landmarks):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 3, (0, 255, 0), cv2.FILLED)
        return img

    def get_landmark_data(self):
        if self.results and self.results.hand_landmarks:
            my_hand = self.results.hand_landmarks[0]
            lm_list = []
            for lm in my_hand:
                lm_list.extend([lm.x, lm.y, lm.z])
            return lm_list
        return None

    def close(self):
        self.detector.close()
