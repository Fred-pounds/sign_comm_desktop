import os
import numpy as np
import sounddevice as sd
import cv2
from PIL import Image
import json
import threading
import queue
import customtkinter as ctk

from app.theme import Theme, AppColors
from app.services.speech_recognizer import SpeechRecognizer
from app.services.sign_generator import SignGenerator

class SpeechToSignView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.speech_recognizer = SpeechRecognizer()
        self.sign_generator = SignGenerator()
        
        # UI Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(self, text="Speech to Sign", font=Theme.get_title_font(), text_color=AppColors.PRIMARY)
        self.header.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1) # Mic/Text
        self.content_frame.grid_columnconfigure(1, weight=3) # Video Playback
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Left side: Mic & Text
        self.mic_frame = Theme.create_glass_frame(self.content_frame)
        self.mic_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.mic_frame.grid_rowconfigure(1, weight=1)
        
        self.record_btn = ctk.CTkButton(self.mic_frame, text="🎤 Start Recording", font=Theme.get_heading_font(),
                                        fg_color=AppColors.PRIMARY, text_color=AppColors.BACKGROUND,
                                        height=60, command=self.toggle_recording)
        self.record_btn.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        
        self.transcription_var = ctk.StringVar(value="Waiting for speech...")
        self.transcription_label = ctk.CTkLabel(self.mic_frame, textvariable=self.transcription_var, 
                                                font=Theme.get_heading_font(),
                                                text_color=AppColors.TEXT_PRIMARY,
                                                wraplength=200)
        self.transcription_label.grid(row=1, column=0, pady=20, padx=20, sticky="n")
        
        # Right side: Video Player
        self.video_frame = Theme.create_glass_frame(self.content_frame)
        self.video_frame.grid(row=0, column=1, sticky="nsew")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="Sign Video Output", font=Theme.get_title_font())
        self.video_label.grid(row=0, column=0, sticky="nsew")

        # Audio & Transcription Queue
        self.msg_queue = queue.Queue()
        
        # Audio recording state
        self.is_recording = False
        self.audio_stream = None
        
        # Video playback state
        self.is_playing = False
        self.video_queue = []
        self.current_cap = None
        
        # Start polling for messages
        self.poll_transcription_queue()

    def poll_transcription_queue(self):
        """Polls the queue for messages from the audio callback thread"""
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                text = msg.get("text", "")
                is_final = msg.get("is_final", False)
                print(f"DEBUG: [poll] Got message: text='{text}', is_final={is_final}")
                self.handle_transcription(text, is_final)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.poll_transcription_queue)

    def audio_callback(self, indata, frames, time, status):
        """Called by sounddevice for each audio buffer slice"""
        # Entry check
        # print("DEBUG: audio_callback triggered") 
        
        if status:
            print(f"DEBUG: Audio status: {status}")
        
        # Calculate volume level for debugging
        volume_norm = np.linalg.norm(indata) * 10
        if volume_norm > 0: 
            # print(f"DEBUG: Audio level detected: {volume_norm:.4f}")
            pass
        
        # Vosk expects 16-bit PCM, flattened
        audio_int16 = (indata.flatten() * 32767).astype(np.int16).tobytes()
        
        try:
            result_dict = self.speech_recognizer.transcribe_chunk(audio_int16)
        except Exception as e:
            print(f"DEBUG: Error in transcribe_chunk: {e}")
            return
        
        if result_dict:
            text = result_dict.get("text", "")
            is_final = result_dict.get("is_final", False)
            
            # Even if text is empty, print for debugging if it's final
            if text or is_final:
                print(f"DEBUG: [audio_callback] Vosk result: '{text}' (final={is_final})")
                # Add to queue instead of calling after() directly from thread
                self.msg_queue.put({"text": text, "is_final": is_final})

    def handle_transcription(self, text, is_final):
        print(f"DEBUG: [handle_transcription] entry: text='{text}', is_final={is_final}")
        if not text:
            if is_final:
                 # Still do mapping check if final even if text is empty? 
                 # Actually Vosk final empty results are just silence.
                 print("DEBUG: [handle_transcription] Final but empty text, skipping.")
            return
        # Show what we're hearing
        self.transcription_var.set(f"Heard:\n{text}")
        
        if is_final:
            print(f"DEBUG: [handle_transcription] FINAL transcription received: '{text}'")
            # Generate sequence of video paths
            sequence = self.sign_generator.get_sign_sequence(text)
            if sequence:
                print(f"DEBUG: Mapped to sequence: {[s['word'] for s in sequence]}")
                for item in sequence:
                    # FIX: Removed deduplication check to allow repeated words (e.g. "hello hello")
                    self.video_queue.append(item['asset'])
                
                if not self.is_playing:
                    print(f"DEBUG: Starting playback of {len(self.video_queue)} items")
                    self.play_next_video()
            elif text:
                print(f"DEBUG: No sign matches found for text: '{text}'")

    def toggle_recording(self):
        if self.is_recording:
            # Stop
            print("DEBUG: Stopping recording and finalizing transcription...")
            self.is_recording = False
            self.record_btn.configure(text="🎤 Start Recording", fg_color=AppColors.PRIMARY)
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()
            
            # Force final result check after stopping stream
            try:
                # Giving a very small silent buffer can sometimes help Vosk finalize
                final_res = self.speech_recognizer.recognizer.Result()
                res_dict = json.loads(final_res)
                text = res_dict.get("text", "")
                if text:
                    print(f"DEBUG: Final transcription on stop: '{text}'")
                    self.handle_transcription(text, True)
            except Exception as e:
                print(f"DEBUG: Could not get final result on stop: {e}")

            self.transcription_var.set(self.transcription_var.get() + "\n[Stopped]")
        else:
            # Start
            self.is_recording = True
            self.record_btn.configure(text="⏹️ Stop Recording", fg_color=AppColors.ERROR)
            self.transcription_var.set("Listening...")
            
            # Start stream
            print("DEBUG: Starting audio stream on default device...")
            try:
                self.audio_stream = sd.InputStream(samplerate=16000, 
                                                   channels=1, 
                                                   dtype='float32', 
                                                   blocksize=4000, # ~250ms chunks for Vosk
                                                   callback=self.audio_callback)
                self.audio_stream.start()
                print("DEBUG: Audio stream started.")
            except Exception as e:
                print(f"DEBUG: Failed to start audio stream: {e}")
                self.is_recording = False
                self.record_btn.configure(text="🎤 Start Recording", fg_color=AppColors.PRIMARY)
                self.transcription_var.set("Error starting mic")

    def play_next_video(self):
        if not self.video_queue:
            self.is_playing = False
            self.video_label.configure(image=None, text="Sign Video Output")
            return
            
        self.is_playing = True
        video_path = self.video_queue.pop(0)
        
        if not os.path.exists(video_path):
            print(f"DEBUG: Video file NOT FOUND: {video_path}")
            self.play_next_video()
            return

        print(f"DEBUG: Playing video: {video_path}")
        self.current_cap = cv2.VideoCapture(video_path)
        if not self.current_cap.isOpened():
            print(f"DEBUG: Failed to open video: {video_path}")
            self.play_next_video()
            return
            
        self.update_video_frame()
        
    def update_video_frame(self):
        if not self.is_playing or not self.current_cap:
            return
            
        w, h = self.video_label.winfo_width(), self.video_label.winfo_height()
        
        # If the widget isn't fully rendered yet (1x1), don't read the frame.
        # Just wait and try again so we don't lose the video content.
        if w <= 10 or h <= 10:
            # print("DEBUG: Waiting for layout (size too small)...")
            self.after(50, self.update_video_frame)
            return

        ret, frame = self.current_cap.read()
        if ret:
            # Display frame
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(color_frame)
            
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(w, h))
            self.video_label.configure(image=ctk_image, text="")
            # Keep a reference to prevent garbage collection
            self.video_label.image = ctk_image

            self.after(33, self.update_video_frame) # ~30fps
        else:
            # End of video
            self.current_cap.release()
            self.current_cap = None
            self.play_next_video()

    def stop_all(self):
        if self.is_recording and self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            
        self.is_playing = False
        self.video_queue.clear()
        if self.current_cap:
            self.current_cap.release()

    def destroy(self):
        self.stop_all()
        super().destroy()
