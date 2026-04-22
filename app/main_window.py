import customtkinter as ctk
from PIL import Image
import os

from .theme import AppColors, Theme

from .views.sign_to_speech_view import SignToSpeechView
from .views.speech_to_sign_view import SpeechToSignView

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=AppColors.BACKGROUND, **kwargs)
        
        # Grid layout: 1 row, 2 columns (sidebar | content)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=AppColors.SURFACE)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1) # Push logo to top, buttons below
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SignComm", font=Theme.get_title_font(), text_color=AppColors.PRIMARY)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.subtitle = ctk.CTkLabel(self.sidebar, text="Desktop Edition", font=Theme.get_small_font(), text_color=AppColors.TEXT_SECONDARY)
        self.subtitle.grid(row=1, column=0, padx=20, pady=(0, 30))
        
        # Navigation Buttons
        self.btn_sign = ctk.CTkButton(
            self.sidebar, 
            text="🗣️ Sign to Speech", 
            font=Theme.get_heading_font(),
            height=50,
            fg_color="transparent",
            text_color=AppColors.TEXT_SECONDARY,
            hover_color="#333333",
            anchor="w",
            command=lambda: self.select_view("sign")
        )
        self.btn_sign.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_speech = ctk.CTkButton(
            self.sidebar, 
            text="🤟 Speech to Sign", 
            font=Theme.get_heading_font(),
            height=50,
            fg_color="transparent",
            text_color=AppColors.TEXT_SECONDARY,
            hover_color="#333333",
            anchor="w",
            command=lambda: self.select_view("speech")
        )
        self.btn_speech.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Settings / Status at bottom
        self.status_label = ctk.CTkLabel(self.sidebar, text="Models Loaded", font=Theme.get_small_font(), text_color=AppColors.SECONDARY)
        self.status_label.grid(row=5, column=0, padx=20, pady=20)
        
        # 2. Main Content Area
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        # Initialize views
        self.views = {}
        
        self.view_sign = SignToSpeechView(self.content_area)
        self.view_speech = SpeechToSignView(self.content_area)
        
        self.views["sign"] = self.view_sign
        self.views["speech"] = self.view_speech
        
        self.current_view = None
        
        # Default selection
        self.select_view("sign")

    def select_view(self, view_name):
        if self.current_view == view_name:
            return
            
        # Update button colors
        self.btn_sign.configure(fg_color=AppColors.PRIMARY if view_name == "sign" else "transparent", 
                                text_color=AppColors.BACKGROUND if view_name == "sign" else AppColors.TEXT_SECONDARY)
        self.btn_speech.configure(fg_color=AppColors.PRIMARY if view_name == "speech" else "transparent",
                                  text_color=AppColors.BACKGROUND if view_name == "speech" else AppColors.TEXT_SECONDARY)
        
        # Hide current view
        if self.current_view and self.current_view in self.views:
            old_view = self.views[self.current_view]
            old_view.grid_forget()
            if hasattr(old_view, 'stop_camera'):
                old_view.stop_camera()
            if hasattr(old_view, 'stop_all'):
                old_view.stop_all()
            
        # Show new view
        self.current_view = view_name
        new_view = self.views[view_name]
        new_view.grid(row=0, column=0, sticky="nsew")
        if hasattr(new_view, 'start_camera'):
            new_view.start_camera()
