# =============================================================================
# MAIN.PY - APPLICATION ENTRYPOINT & NEOBRUTALIST DESKTOP OS SHELL
# =============================================================================
# Architecture Overview:
#   This module launches the desktop operating environment:
#     🍋 HERTZ2HERTZ - Lemon Beach Edition 🍋
#   It synthesizes a modern K-Pop summer photobook aesthetic with Neobrutalism:
#     - Pastel Summer Sky Cyan (#BAE6FD)
#     - Sunshine Lemon Yellow (#FEF08A)
#     - Mint Seafoam Green (#A7F3D0)
#     - Coral Flamingo Pink (#FBCFE8)
#     - Stark 4px solid borders with zero corner radii (corner_radius=0)
#     - Clean bold typography (Helvetica / Courier New)
#
# Navigation & Lifecycle Architecture:
#   1. Lock Screen: HERTZ2HERTZ brand header, album meta tags, profile selector.
#   2. Wipe Transition: Animated full-screen sweep creating a seamless retro transition.
#   3. Desktop Workspace: Icon grid launching sub-windows inside RetroWindow wrappers.
#   4. Taskbar: Logout controls, album branding, and live MATLAB Engine monitor.
# =============================================================================

import customtkinter as ctk
import time
import os
from PIL import Image
from retro_ui import (
    RetroWindow, RetroLoadingBar, RETRO_FONT, TITLE_FONT, PIXEL_FONT_LARGE,
    HERTZ_SKY_BLUE, HERTZ_LEMON_YELLOW, HERTZ_MINT_GREEN, HERTZ_CORAL_PINK,
    HERTZ_DEEP_BLUE, HERTZ_WARM_WHITE
)
from dc_ac_circuits_engine import DCAcCircuitsEngine
from rf_engineering_engine import RFEngineeringEngine
from logic_circuits_engine import LogicCircuitsEngine
from learning_hub import LearningHub
from about_page import AboutPage
from electrical_circuits_engine import ElectricalCircuitsEngine
from matlab_utils import matlab_manager

class MainApp(ctk.CTk):
    """
    Root application window representing the desktop operating system.
    Manages screen transitions, window stacking, desktop icons, and engine instances.
    """
    def __init__(self):
        super().__init__()
        
        self.title("HERTZ2HERTZ - Engineering & Simulation Suite")
        self.geometry("1240x820")
        self.configure(fg_color=HERTZ_SKY_BLUE) # Lemon Beach Sky Blue
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Two primary top-level views: Lock Screen and Desktop Workspace
        self.lock_screen = ctk.CTkFrame(self, fg_color=HERTZ_SKY_BLUE, corner_radius=0)
        self.desktop = ctk.CTkFrame(self, fg_color=HERTZ_SKY_BLUE, corner_radius=0)
        
        self.build_lock_screen()
        self.build_desktop()
        self.lock_screen.grid(row=0, column=0, sticky="nsew")
        
        # Transition Overlay Frame (Initially Hidden off-screen)
        self.wipe_frame = ctk.CTkFrame(self, fg_color=HERTZ_LEMON_YELLOW, corner_radius=0, border_width=4, border_color="#000000")
        self.is_animating = False

    def build_lock_screen(self):
        self.lock_screen.grid_rowconfigure(0, weight=1)
        self.lock_screen.grid_rowconfigure(6, weight=1)
        self.lock_screen.grid_columnconfigure(0, weight=1)
        
        # Decorative Brutalist Header - HERTZ2HERTZ Concept
        title_box = ctk.CTkFrame(self.lock_screen, fg_color="transparent")
        title_box.grid(row=1, column=0, pady=(20, 10))

        # Top Barcode & Album Tag Line
        top_meta = ctk.CTkFrame(title_box, fg_color=HERTZ_LEMON_YELLOW, border_width=4, border_color="#000000", corner_radius=0)
        top_meta.pack(pady=(0, 10))
        ctk.CTkLabel(
            top_meta, 
            text=" ║▌║█║▌│║▌║▌█║   HERTZ2HERTZ   •   LEMON EDITION   •  NUMERICAL ANALYSIS LAB   ", 
            font=("Courier New", 12, "bold"), 
            text_color="#000000"
        ).pack(padx=16, pady=5)

        # Main Title Banner: HERTZ2HERTZ (Massive Neobrutalist Lemon Vibe)
        shadow_frame = ctk.CTkFrame(title_box, fg_color="#000000", corner_radius=0)
        shadow_frame.pack(pady=15)
        
        # Outer box uses Mint Green to contrast the Lemon Yellow
        title_frame = ctk.CTkFrame(shadow_frame, fg_color=HERTZ_LEMON_YELLOW, border_width=8, border_color="#000000", corner_radius=0)
        title_frame.pack(padx=(0, 15), pady=(0, 15))
        
        # HERTZ2HERTZ Title
        title = ctk.CTkLabel(
            title_frame, 
            text=" HERTZ2HERTZ ", 
            font=("Arial Black", 85, "bold"), 
            text_color="#000000"  # Citrus Orange to give it a strong Lemon/Summer vibe
        )
        title.pack(padx=30, pady=(20, 0))
        
        subtitle = ctk.CTkLabel(
            title_frame, 
            text="", 
            font=("Helvetica", 16, "bold"), 
            text_color="#0284C7"  # Deep Coastal Blue
        )
        subtitle.pack(padx=30, pady=(0, 25))

        # Decorative concept pill tags inspired by Lemon Tang photobook
        tag_frame = ctk.CTkFrame(title_box, fg_color="transparent")
        tag_frame.pack(pady=(8, 18))
        
        tag1 = ctk.CTkLabel(tag_frame, text=" [ ELECTRICAL ] ", font=("Helvetica", 11, "bold"), fg_color=HERTZ_LEMON_YELLOW, text_color="#000000", corner_radius=0)
        tag1.pack(side="left", padx=6)
        
        tag2 = ctk.CTkLabel(tag_frame, text=" [ ELECTRONICS ] ", font=("Helvetica", 11, "bold"), fg_color=HERTZ_CORAL_PINK, text_color="#000000", corner_radius=0)
        tag2.pack(side="left", padx=6)
        
        tag3 = ctk.CTkLabel(tag_frame, text=" [ MATLAB & PYTHON CALCULATOR ] ", font=("Helvetica", 11, "bold"), fg_color=HERTZ_MINT_GREEN, text_color="#000000", corner_radius=0)
        tag3.pack(side="left", padx=6)
        
        users_frame = ctk.CTkFrame(self.lock_screen, fg_color="transparent")
        users_frame.grid(row=2, column=0, pady=(10, 20))
        
        self.create_login_btn(users_frame, "SOLVE\n[CALCULATOR]", HERTZ_LEMON_YELLOW, lambda: self.trigger_transition(lambda: self.login("SOLVE")))
        self.create_login_btn(users_frame, "LEARN\n[STUDY HUB]", "#FFFFFF", lambda: self.trigger_transition(lambda: self.login("LEARN")))
        self.create_login_btn(users_frame, "ABOUT\n[PROFILES]", HERTZ_CORAL_PINK, lambda: self.trigger_transition(lambda: self.login("ABOUT")))
        
    def create_login_btn(self, parent, text, color, command):
        # Neobrutal blocky buttons with huge fonts
        btn = ctk.CTkButton(
            parent, 
            text=text, 
            font=("Helvetica", 24, "bold"), 
            fg_color=color, 
            text_color="#000000", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            hover_color="#FFFFFF", 
            width=230, 
            height=200, 
            command=command
        )
        btn.pack(side="left", padx=16)

    def trigger_transition(self, swap_cmd):
        """Animates a solid colored block sweeping across the screen, running swap_cmd when covered."""
        if self.is_animating: return
        self.is_animating = True
        
        # Start wipe off-screen left
        self.wipe_frame.place(relx=-1.0, rely=0, relwidth=1.0, relheight=1.0)
        self.wipe_frame.lift()
        
        self.animate_wipe_in(0, swap_cmd)
        
    def animate_wipe_in(self, step, swap_cmd):
        """Slide from -1.0 to 0.0"""
        relx = -1.0 + (step * 0.1)
        if step <= 10:
            self.wipe_frame.place_configure(relx=relx)
            self.after(15, lambda: self.animate_wipe_in(step+1, swap_cmd))
        else:
            self.wipe_frame.place_configure(relx=0.0)
            swap_cmd() # DO THE UI SWAP
            self.after(100, lambda: self.animate_wipe_out(0))
            
    def animate_wipe_out(self, step):
        """Slide from 0.0 to 1.0"""
        relx = (step * 0.1)
        if step <= 10:
            self.wipe_frame.place_configure(relx=relx)
            self.after(15, lambda: self.animate_wipe_out(step+1))
        else:
            self.wipe_frame.place_forget()
            self.is_animating = False

    def login(self, profile):
        self.lock_screen.grid_forget()
        self.desktop.grid(row=0, column=0, sticky="nsew")
        
        for widget in self.icons_frame.winfo_children():
            widget.destroy()
            
        self.icons_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.workspace.grid_forget()
        
        if profile == "SOLVE":
            self.create_desktop_icon("⚡ EE", HERTZ_LEMON_YELLOW, 0, 0, lambda: self.trigger_transition(lambda: self.open_app("EE")))
            self.create_desktop_icon("🌊 ECE", HERTZ_MINT_GREEN, 0, 1, lambda: self.trigger_transition(lambda: self.open_app("DC/AC")))
            self.create_desktop_icon("📡 RF TOOLBOX", HERTZ_CORAL_PINK, 0, 2, lambda: self.trigger_transition(lambda: self.open_app("RF")))
            self.create_desktop_icon("🖩 LOGIC", "#FFFFFF", 0, 3, lambda: self.trigger_transition(lambda: self.open_app("LOGIC")))
        elif profile == "LEARN":
            self.create_desktop_icon("📚 LEARN HUB", HERTZ_LEMON_YELLOW, 0, 0, lambda: self.trigger_transition(lambda: self.open_app("HUB")))
        elif profile == "ABOUT":
            self.create_desktop_icon("👥 DEVELOPERS", HERTZ_CORAL_PINK, 0, 0, lambda: self.trigger_transition(lambda: self.open_app("ABOUT")))

    def build_desktop(self):
        self.desktop.grid_rowconfigure(0, weight=1)
        self.desktop.grid_columnconfigure(0, weight=1)
        
        # Desktop Icons Area
        self.icons_frame = ctk.CTkFrame(self.desktop, fg_color="transparent")
        self.icons_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Window Workspace (Hidden initially)
        self.workspace = ctk.CTkFrame(self.desktop, fg_color="transparent")
        self.workspace.grid_rowconfigure(0, weight=1)
        self.workspace.grid_columnconfigure(0, weight=1)
        
        self.apps = {}
        self.apps["EE"] = RetroWindow(self.workspace, title="EE FUNDAMENTALS", theme_color=HERTZ_LEMON_YELLOW, close_cmd=lambda: self.trigger_transition(lambda: self.close_app("EE")))
        ElectricalCircuitsEngine(self.apps["EE"].content).pack(fill="both", expand=True)

        self.apps["DC/AC"] = RetroWindow(self.workspace, title="ECE SEMICONDUCTORS", theme_color=HERTZ_MINT_GREEN, close_cmd=lambda: self.trigger_transition(lambda: self.close_app("DC/AC")))
        DCAcCircuitsEngine(self.apps["DC/AC"].content).pack(fill="both", expand=True)
        
        self.apps["RF"] = RetroWindow(self.workspace, title="RF ENGINEERING", theme_color=HERTZ_CORAL_PINK, close_cmd=lambda: self.trigger_transition(lambda: self.close_app("RF")))
        RFEngineeringEngine(self.apps["RF"].content).pack(fill="both", expand=True)

        self.apps["LOGIC"] = RetroWindow(self.workspace, title="LOGIC CIRCUITS", theme_color=HERTZ_LEMON_YELLOW, close_cmd=lambda: self.trigger_transition(lambda: self.close_app("LOGIC")))
        LogicCircuitsEngine(self.apps["LOGIC"].content).pack(fill="both", expand=True)
        
        self.apps["HUB"] = RetroWindow(self.workspace, title="LEARNING HUB", theme_color="#BAE6FD", close_cmd=lambda: self.trigger_transition(lambda: self.close_app("HUB")))
        LearningHub(self.apps["HUB"].content).pack(fill="both", expand=True)
        
        self.apps["ABOUT"] = RetroWindow(self.workspace, title="ABOUT", theme_color=HERTZ_CORAL_PINK, close_cmd=lambda: self.trigger_transition(lambda: self.close_app("ABOUT")))
        AboutPage(self.apps["ABOUT"].content).pack(fill="both", expand=True)
        
        # Taskbar
        self.taskbar = ctk.CTkFrame(self.desktop, fg_color="#000000", height=50, corner_radius=0)
        self.taskbar.grid(row=1, column=0, sticky="ew")
        
        start_btn = ctk.CTkButton(
            self.taskbar, 
            text=" 🍋 HERTZ2HERTZ [LOGOUT] ", 
            font=RETRO_FONT, 
            fg_color=HERTZ_LEMON_YELLOW, 
            text_color="#000000", 
            border_width=3, 
            border_color="#FFFFFF", 
            corner_radius=0, 
            hover_color="#FFFFFF", 
            command=lambda: self.trigger_transition(self.logout)
        )
        start_btn.pack(side="left", padx=10, pady=5)

        # Status badge for MATLAB Engine in taskbar
        self.matlab_status_lbl = ctk.CTkLabel(
            self.taskbar,
            text="[MATLAB: INITIALIZING...]",
            font=("Courier New", 11, "bold"),
            text_color="#FEF08A"
        )
        self.matlab_status_lbl.pack(side="right", padx=15)
        self.update_matlab_status()

    def update_matlab_status(self):
        status_txt = matlab_manager.get_status_text()
        self.matlab_status_lbl.configure(text=status_txt, text_color="#A7F3D0")
        self.after(3000, self.update_matlab_status)

    def create_desktop_icon(self, text, color, row, col, command):
        btn = ctk.CTkButton(
            self.icons_frame, 
            text=text, 
            font=("Helvetica", 15, "bold"), 
            fg_color=color, 
            text_color="#000000", 
            hover_color="#FFFFFF", 
            width=190, 
            height=180, 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            command=command
        )
        btn.grid(row=row, column=col, padx=25, pady=30)

    def open_app(self, app_name):
        """Hides icons and expands the requested app."""
        self.icons_frame.grid_forget()
        self.workspace.grid(row=0, column=0, sticky="nsew", padx=40, pady=25)
        for name, window in self.apps.items():
            if name == app_name:
                window.grid(row=0, column=0, sticky="nsew")
            else:
                window.grid_forget()
                
    def close_app(self, app_name):
        """Closes the app and shows the desktop icons again."""
        self.apps[app_name].grid_forget()
        self.workspace.grid_forget()
        self.icons_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
    def logout(self):
        """Returns to lock screen."""
        self.desktop.grid_forget()
        self.lock_screen.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

