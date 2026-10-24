import customtkinter as ctk
import time
import threading

# NEOBRUTALISM TYPOGRAPHY
RETRO_FONT = ("Helvetica", 14, "bold")
TITLE_FONT = ("Helvetica", 18, "bold")
PIXEL_FONT_LARGE = ("Arial Black", 32, "bold")

# NEOBRUTALISM COLORS
ACCENT_BLUE = "#0055FF"
BG_WHITE = "#F5F5F0"
BORDER_BLACK = "#000000"

# HERTZ2HERTZ "LEMON BEACH" AESTHETIC PALETTE
HERTZ_SKY_BLUE = "#BAE6FD"      # Pastel Summer Sky Cyan
HERTZ_LEMON_YELLOW = "#FEF08A"  # Lemon Tang Sunshine Yellow
HERTZ_MINT_GREEN = "#A7F3D0"    # Mint Seafoam Green
HERTZ_CORAL_PINK = "#FBCFE8"    # Pastel Flamingo Pink
HERTZ_DEEP_BLUE = "#0284C7"     # Vibrant Coastal Accent Blue
HERTZ_WARM_WHITE = "#FEFCE8"    # Soft Warm Lemon White

class RetroWindow(ctk.CTkFrame):
    """
    A custom frame that mimics Neobrutalist web design.
    Features a hard, solid black drop shadow, extremely thick black borders, 
    and blocky, stark geometry.
    """
    def __init__(self, master, title="WINDOW", theme_color=ACCENT_BLUE, close_cmd=None, **kwargs):
        # Base frame acts as the black drop-shadow (Hard 6px offset)
        super().__init__(master, fg_color=BORDER_BLACK, corner_radius=0, **kwargs)
        
        # Main foreground frame
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_WHITE, border_width=4, border_color=BORDER_BLACK, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=(0, 6), pady=(0, 6))
        
        # Brutalist Title Header
        self.title_bar = ctk.CTkFrame(self.main_frame, fg_color=theme_color, height=45, corner_radius=0, border_width=4, border_color=BORDER_BLACK)
        self.title_bar.pack(fill="x", padx=0, pady=0) # Flush to the edges
        self.title_bar.pack_propagate(False)
        
        # Text
        text_fg = "#000000" if theme_color in [HERTZ_LEMON_YELLOW, HERTZ_MINT_GREEN, HERTZ_CORAL_PINK, HERTZ_SKY_BLUE, "#FFDC00"] else "#FFFFFF"
        self.lbl_title = ctk.CTkLabel(self.title_bar, text=f" {title.upper()} ", font=TITLE_FONT, text_color=text_fg)
        self.lbl_title.pack(side="left", padx=15, pady=2)
        
        # Big blocky Close Button
        red_btn = ctk.CTkButton(self.title_bar, width=40, height=40, text="X", font=TITLE_FONT, fg_color="#FF3333", text_color="#000000", border_width=4, border_color=BORDER_BLACK, corner_radius=0, hover_color="#FFFFFF", command=close_cmd)
        red_btn.pack(side="right", padx=0, pady=0)
        
        # Content Area 
        self.content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

class RetroLoadingBar(ctk.CTkLabel):
    """
    Animated retro loading bar. e.g., Loading... [||||      ]
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, text="Loading... 00000000", font=RETRO_FONT, text_color="#000000", **kwargs)
        self.is_animating = True
        self.animate_loading()
        
    def animate_loading(self):
        if not self.is_animating:
            return
            
        current_text = self.cget("text")
        if "00000000000000000000" in current_text:
            self.configure(text="Loading... ")
        else:
            self.configure(text=current_text.replace("Loading... ", "Loading... 0").replace("0", "00", 1))
            
        self.after(300, self.animate_loading)
