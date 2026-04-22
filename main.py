import customtkinter as ctk
import os
import sys
import sounddevice as sd

# Add the project root to the path so we can import app modules properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.theme import setup_theme, Theme, AppColors
from app.main_window import MainWindow

def main():
    print("--- Audio Devices Found ---")
    try:
        print(sd.query_devices())
        print(f"Default Input Device: {sd.default.device[0]}")
    except Exception as e:
        print(f"Could not query audio devices: {e}")
    print("---------------------------")
    setup_theme()
    
    app = ctk.CTk()
    app.title("Sign-Speech Communication Sys")
    app.geometry("1100x700")
    app.minsize(900, 600)
    app.configure(fg_color=AppColors.BACKGROUND)
    
    # Center window on screen
    app.update_idletasks()
    width = app.winfo_width()
    frm_width = app.winfo_rootx() - app.winfo_x()
    win_width = width + 2 * frm_width
    height = app.winfo_height()
    titlebar_height = app.winfo_rooty() - app.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = app.winfo_screenwidth() // 2 - win_width // 2
    y = app.winfo_screenheight() // 2 - win_height // 2
    app.geometry(f'{width}x{height}+{x}+{y}')

    main_window = MainWindow(master=app)
    main_window.pack(fill="both", expand=True)
    
    app.mainloop()

if __name__ == "__main__":
    main()
