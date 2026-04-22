import customtkinter as ctk

class AppColors:
    # Modern Dark Theme Colors
    BACKGROUND = "#121212"
    SURFACE = "#1E1E1E"
    PRIMARY = "#BB86FC"
    SECONDARY = "#03DAC6"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B3B3B3"
    ERROR = "#CF6679"

def setup_theme():
    """Configures the global CustomTkinter theme."""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue") # We will override specific colors where needed

class Theme:
    """Helper class for applying consistent styling to widgets."""
    
    @staticmethod
    def get_title_font():
        return ctk.CTkFont(family="Inter", size=24, weight="bold")
    
    @staticmethod
    def get_heading_font():
        return ctk.CTkFont(family="Inter", size=18, weight="bold")
    
    @staticmethod
    def get_body_font():
        return ctk.CTkFont(family="Inter", size=14)
        
    @staticmethod
    def get_small_font():
        return ctk.CTkFont(family="Inter", size=12)

    @staticmethod
    def create_glass_frame(master, **kwargs):
        """Creates a frame with styling that mimics a glass panel/surface."""
        return ctk.CTkFrame(
            master,
            fg_color=AppColors.SURFACE,
            corner_radius=12,
            border_width=1,
            border_color="#333333",
            **kwargs
        )
