import customtkinter as ctk
import cv2
from PIL import Image
import threading
import pyttsx3

from app.theme import Theme, AppColors
from app.services.hand_tracker import HandTracker
from app.services.gesture_recognizer import GestureRecognizer

class SignToSpeechView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.tracker = HandTracker()
        self.recognizer = GestureRecognizer()
        
        self.engine = pyttsx3.init()
        
        # UI Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(self, text="Sign to Speech", font=Theme.get_title_font(), text_color=AppColors.PRIMARY)
        self.header.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=3) # Camera
        self.content_frame.grid_columnconfigure(1, weight=1) # Results
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Left side: Camera feed
        self.camera_frame = Theme.create_glass_frame(self.content_frame)
        self.camera_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.camera_frame.grid_rowconfigure(0, weight=1)
        self.camera_frame.grid_columnconfigure(0, weight=1)
        
        self.video_label = ctk.CTkLabel(self.camera_frame, text="Starting camera...")
        self.video_label.grid(row=0, column=0, sticky="nsew")
        
        # Right side: Results & controls
        self.results_frame = Theme.create_glass_frame(self.content_frame)
        self.results_frame.grid(row=0, column=1, sticky="nsew")
        self.results_frame.grid_rowconfigure(1, weight=1)
        
        self.results_title = ctk.CTkLabel(self.results_frame, text="Predicted Sign", font=Theme.get_heading_font())
        self.results_title.grid(row=0, column=0, pady=20, padx=20)
        
        # Prediction display
        self.prediction_var = ctk.StringVar(value="Waiting...")
        self.prediction_label = ctk.CTkLabel(self.results_frame, textvariable=self.prediction_var, 
                                             font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                                             text_color=AppColors.SECONDARY,
                                             wraplength=200)
        self.prediction_label.grid(row=1, column=0, pady=20, padx=20)
        
        # Speak button
        self.speak_btn = ctk.CTkButton(self.results_frame, text="🗣️ Speak", font=Theme.get_heading_font(),
                                       fg_color=AppColors.PRIMARY, text_color=AppColors.BACKGROUND,
                                       height=50, command=self.speak_prediction)
        self.speak_btn.grid(row=2, column=0, pady=20, padx=20, sticky="ew")
        
        self.cap = None
        self.is_running = False
        self.last_spoken_text = ""

    def speak_prediction(self):
        text = self.prediction_var.get()
        if text and text != "Waiting..." and not text.startswith("Analyzing") and text != "No hand detected":
            threading.Thread(target=self._speak, args=(text,), daemon=True).start()
            
    def _speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def start_camera(self):
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            self.is_running = True
            self.update_frame()
            
    def stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.video_label.configure(image=None, text="Camera stopped")
            
    def update_frame(self):
        if not self.is_running or not self.cap.isOpened():
            return
            
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1) # Mirror
            
            self.tracker.find_hands(frame)
            frame = self.tracker.draw_hands(frame)
            
            lm_list = self.tracker.get_landmark_data()
            if lm_list:
                prediction = self.recognizer.process_landmarks(lm_list)
                if prediction:
                    pred_text = prediction["text"]
                    self.prediction_var.set(pred_text)
                    
                    if pred_text != self.last_spoken_text:
                        self.last_spoken_text = pred_text
                        self.speak_prediction()
                else:
                    self.prediction_var.set("Waiting...")
            else:
                self.prediction_var.set("No hand detected")
                self.recognizer.clear()
                self.last_spoken_text = ""

            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(color_frame)
            
            w, h = self.video_label.winfo_width(), self.video_label.winfo_height()
            if w > 10 and h > 10:
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(w, h))
                self.video_label.configure(image=ctk_image, text="")
                # FIX: Keep reference to prevent garbage collection and TclError
                self.video_label.image = ctk_image
            else:
                # Wait for layout if too small
                self.after(50, self.update_frame)
                return

        self.after(30, self.update_frame)

    def destroy(self):
        self.stop_camera()
        self.tracker.close()
        super().destroy()
