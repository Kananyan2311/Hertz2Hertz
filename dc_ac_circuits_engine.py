# =============================================================================
# DC_AC_CIRCUITS_ENGINE.PY - SEMICONDUCTOR ELECTRONICS & SIMULATION ENGINE
# =============================================================================
# Architecture Overview:
#   This module implements the user interface and circuit simulation pipeline
#   for the Electronic Circuit Analysis course (ECELXC30):
#     I.   Diode Calculator (Shockley I-V, AC dynamic & DC static resistances)
#     II.  Diode Applications (Half/Full Wave Rectifiers, Clippers, Clampers, LED)
#     III. BJT Fundamentals (Ib, Ic, Ie, Beta, Vbe, Vce, Isat)
#     IV.  BJT DC Biasing (Fixed, Divider, Emitter, Feedback topologies & DC Load Lines)
#     V.   BJT AC Small-Signal Analysis (re model, Zin, Zout, Av)
#     VI.  FET Fundamentals & CMOS (JFET, D-MOSFET, E-MOSFET, CMOS Inverter)
#     VII. 3D Transistor Surface Plotting
#
# Integration with MATLAB Engine:
#   Complex non-linear diode equations, BJT bias solving, and FET parabolic models
#   are computed by `matlab_manager` invoking `matlab_code/semiconductor_calc.m`
#   on the official MATLAB Engine (R2026b).
# =============================================================================

import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import datetime
import math
import os
from retro_ui import RETRO_FONT
from matlab_utils import matlab_manager

class DCAcCircuitsEngine(ctk.CTkFrame):
    """
    CustomTkinter Frame hosting the Semiconductor Electronics simulator.
    Renders IEEE-standard electronic vector schematics, collects circuit inputs,
    and visualizes non-linear transfer curves.
    """
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Navigation
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#FFF5EE", border_width=4, border_color="#000000")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="⚡ ELECTRONICS", font=RETRO_FONT, text_color="#000000")
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=20)

        # Updated Syllabus Navigation
        self.nav_btns = {}
        self.btn_theory = self.create_nav_btn("I. Diode Calculator", self.show_theory, 1, "theory")
        self.btn_apps = self.create_nav_btn("II. Diode Applications", self.show_diode_apps, 2, "apps")
        self.btn_bjt = self.create_nav_btn("III. BJT Fundamentals", self.show_bjt, 3, "bjt")
        self.btn_dc = self.create_nav_btn("IV. BJT DC Biasing", self.show_bjt_dc, 4, "dc")
        self.btn_ac = self.create_nav_btn("V. BJT AC Small-Signal", self.show_bjt_ac, 5, "ac")
        self.btn_fet = self.create_nav_btn("VI. FET Fundamentals/Amps", self.show_fet, 6, "fet")
        self.btn_3d = self.create_nav_btn("VII. 3D Transistor Surface", self.show_3d_surface, 7, "3d")
        
        # Main content area (Scrollable)
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.calc_history_log = (
            "================================================================================\n"
            "FINAL PROJECT REPORT - DC & AC ELECTRONICS ENGINE\n"
            "STUDENTS: GONZALES, IVAN LAWRENCE F. & LO NIEVA, STEVEN\n"
            "SECTION: BSCPE241B | DATE: OCTOBER 5, 2026 | STATUS: VERIFIED [/]\n"
            "================================================================================\n"
        )
        
        self.show_theory()

    def create_nav_btn(self, text, command, row, key):
        def wrapper():
            self.set_active_nav(key)
            command()
            
        btn = ctk.CTkButton(
            self.sidebar, 
            text=text, 
            font=("Helvetica", 11, "bold"), 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            hover_color="#BAE6FD", 
            anchor="w",
            command=wrapper
        )
        btn.grid(row=row, column=0, padx=8, pady=6, sticky="ew")
        self.nav_btns[key] = btn
        return btn

    def set_active_nav(self, active_key):
        for k, btn in self.nav_btns.items():
            if k == active_key:
                btn.configure(fg_color="#FEF08A", text_color="#000000", border_color="#000000")
            else:
                btn.configure(fg_color="#FFFFFF", text_color="#000000", border_color="#000000")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_retro_title(self, text):
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        title_frame.pack(pady=10)
        ctk.CTkLabel(title_frame, text=text, font=("Helvetica", 18, "bold"), text_color="#000000").pack(padx=14, pady=6)

    def create_toolbar(self, reset_cmd):
        tb = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        tb.pack(fill="x", padx=20, pady=(0, 10))
        
        btn_reset = ctk.CTkButton(
            tb, 
            text="[ RESET DEFAULTS ]", 
            font=("Helvetica", 11, "bold"), 
            fg_color="#FF3333", 
            text_color="#FFFFFF", 
            border_width=3, 
            border_color="#000000", 
            corner_radius=0,
            command=reset_cmd
        )
        btn_reset.pack(side="left", padx=8, pady=6)
        
        btn_exp = ctk.CTkButton(
            tb, 
            text="[ EXPORT REPORT (.TXT/.CSV) ]", 
            font=("Helvetica", 11, "bold"), 
            fg_color="#27C93F", 
            text_color="#000000", 
            border_width=3, 
            border_color="#000000", 
            corner_radius=0,
            command=self.export_report
        )
        btn_exp.pack(side="left", padx=8, pady=6)
        
        self.lbl_tb_status = ctk.CTkLabel(tb, text="", font=("Helvetica", 10, "bold"), text_color="#0055FF")
        self.lbl_tb_status.pack(side="right", padx=10)

    def export_report(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Electronics_Report_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.calc_history_log)
                f.write(f"\nReport Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if hasattr(self, 'lbl_tb_status'):
                self.lbl_tb_status.configure(text=f"Saved: {filename}", text_color="#27C93F")
        except Exception as e:
            if hasattr(self, 'lbl_tb_status'):
                self.lbl_tb_status.configure(text=f"Export Error: {e}", text_color="#FF3333")

    # ==================== IEEE SCHEMATIC SYMBOL HELPERS ====================
    def draw_gnd(self, cvs, x, y):
        """Draws compact standard 3-tier ground symbol"""
        cvs.create_line(x, y, x, y+8, width=2.5, fill="#000000")
        cvs.create_line(x-14, y+8, x+14, y+8, width=3, fill="#000000")
        cvs.create_line(x-9, y+13, x+9, y+13, width=2.5, fill="#000000")
        cvs.create_line(x-4, y+18, x+4, y+18, width=2, fill="#000000")

    def draw_vsource_ac(self, cvs, x, y, label="Vin"):
        """Draws compact AC Sine Voltage source circle with tilde"""
        cvs.create_oval(x-18, y-18, x+18, y+18, fill="#FFFFFF", outline="#000000", width=2.5)
        cvs.create_arc(x-10, y-7, x, y+7, start=0, extent=180, style="arc", width=2, outline="#000000")
        cvs.create_arc(x, y-7, x+10, y+7, start=180, extent=180, style="arc", width=2, outline="#000000")
        if label:
            cvs.create_text(x-24, y, text=label, font=("Helvetica", 11, "bold"), fill="#000000", anchor="e")

    def draw_vsource_dc(self, cvs, x, y, label="Vcc"):
        """Draws compact DC battery symbol"""
        cvs.create_line(x, y-15, x, y-6, width=2.5, fill="#000000")
        cvs.create_line(x-14, y-6, x+14, y-6, width=3.5, fill="#000000") # + plate
        cvs.create_line(x-7, y+4, x+7, y+4, width=5, fill="#000000")     # - plate
        cvs.create_line(x, y+4, x, y+15, width=2.5, fill="#000000")
        cvs.create_text(x+20, y-6, text="+", font=("Helvetica", 12, "bold"), fill="#FF3333")
        cvs.create_text(x+20, y+4, text="-", font=("Helvetica", 12, "bold"), fill="#000000")
        if label:
            cvs.create_text(x-20, y, text=label, font=("Helvetica", 11, "bold"), fill="#000000", anchor="e")

    def draw_cap_h(self, cvs, x1, y, x2, label=""):
        """Draws compact parallel plate horizontal capacitor"""
        mid = (x1 + x2) // 2
        cvs.create_line(x1, y, mid-5, y, width=2.5, fill="#000000")
        cvs.create_line(mid-5, y-14, mid-5, y+14, width=3.5, fill="#000000")
        cvs.create_line(mid+5, y-14, mid+5, y+14, width=3.5, fill="#000000")
        cvs.create_line(mid+5, y, x2, y, width=2.5, fill="#000000")
        if label:
            cvs.create_text(mid, y-22, text=label, font=("Helvetica", 10, "bold"), fill="#000000")

    def draw_res_h(self, cvs, x1, y1, x2, y2, label=""):
        """Draws adaptive horizontal resistor guaranteed to stay strictly within (x1, x2)"""
        span = abs(x2 - x1)
        sign = 1 if x2 >= x1 else -1
        if span < 15:
            cvs.create_line(x1, y1, x2, y2, width=2.5, fill="#000000")
            if label:
                cvs.create_text((x1+x2)/2, y1-14, text=label, font=("Helvetica", 10, "bold"), fill="#000000")
            return
            
        zlen = min(36.0, max(18.0, span * 0.6))
        lead = (span - zlen) / 2.0
        rx1 = x1 + sign * lead
        rx2 = x2 - sign * lead
        amp = min(7.0, zlen / 4.0)
        
        cvs.create_line(x1, y1, rx1, y1, width=2.5, fill="#000000")
        pts = [
            rx1, y1,
            rx1 + sign * zlen * 0.1, y1 - amp,
            rx1 + sign * zlen * 0.3, y1 + amp,
            rx1 + sign * zlen * 0.5, y1 - amp,
            rx1 + sign * zlen * 0.7, y1 + amp,
            rx1 + sign * zlen * 0.9, y1 - amp,
            rx2, y1
        ]
        cvs.create_line(*pts, width=2.5, fill="#000000")
        cvs.create_line(rx2, y1, x2, y2, width=2.5, fill="#000000")
        if label:
            cvs.create_text((x1 + x2) / 2.0, y1 - amp - 10, text=label, font=("Helvetica", 10, "bold"), fill="#000000")

    def draw_res_v(self, cvs, x1, y1, x2, y2, label=""):
        """Draws adaptive vertical resistor guaranteed to stay strictly within (y1, y2)"""
        span = abs(y2 - y1)
        sign = 1 if y2 >= y1 else -1
        if span < 15:
            cvs.create_line(x1, y1, x2, y2, width=2.5, fill="#000000")
            if label:
                cvs.create_text(x1+16, (y1+y2)/2, text=label, font=("Helvetica", 10, "bold"), fill="#000000", anchor="w")
            return
            
        zlen = min(36.0, max(18.0, span * 0.6))
        lead = (span - zlen) / 2.0
        ry1 = y1 + sign * lead
        ry2 = y2 - sign * lead
        amp = min(7.0, zlen / 4.0)
        
        cvs.create_line(x1, y1, x1, ry1, width=2.5, fill="#000000")
        pts = [
            x1, ry1,
            x1 - amp, ry1 + sign * zlen * 0.1,
            x1 + amp, ry1 + sign * zlen * 0.3,
            x1 - amp, ry1 + sign * zlen * 0.5,
            x1 + amp, ry1 + sign * zlen * 0.7,
            x1 - amp, ry1 + sign * zlen * 0.9,
            x1, ry2
        ]
        cvs.create_line(*pts, width=2.5, fill="#000000")
        cvs.create_line(x1, ry2, x2, y2, width=2.5, fill="#000000")
        if label:
            cvs.create_text(x1 + amp + 8, (y1 + y2) / 2.0, text=label, font=("Helvetica", 10, "bold"), fill="#000000", anchor="w")

    def draw_diode_sym(self, cvs, x, y, orient="h", label="D"):
        """Draws compact IEEE diode triangle & cathode bar"""
        if orient == "h":
            cvs.create_line(x-24, y, x-10, y, width=2.5, fill="#000000")
            cvs.create_polygon(x-10, y-12, x-10, y+12, x+10, y, fill="#0055FF", outline="#000000", width=2)
            cvs.create_line(x+10, y-14, x+10, y+14, width=3.5, fill="#000000")
            cvs.create_line(x+10, y, x+24, y, width=2.5, fill="#000000")
            if label:
                cvs.create_text(x, y-20, text=label, font=("Helvetica", 10, "bold"), fill="#000000")
        elif orient == "v_up":
            cvs.create_line(x, y+24, x, y+10, width=2.5, fill="#000000")
            cvs.create_polygon(x-12, y+10, x+12, y+10, x, y-10, fill="#0055FF", outline="#000000", width=2)
            cvs.create_line(x-14, y-10, x+14, y-10, width=3.5, fill="#000000")
            cvs.create_line(x, y-10, x, y-24, width=2.5, fill="#000000")
            if label:
                cvs.create_text(x+20, y, text=label, font=("Helvetica", 10, "bold"), fill="#000000", anchor="w")
        else: # "v_down"
            cvs.create_line(x, y-24, x, y-10, width=2.5, fill="#000000")
            cvs.create_polygon(x-12, y-10, x+12, y-10, x, y+10, fill="#0055FF", outline="#000000", width=2)
            cvs.create_line(x-14, y+10, x+14, y+10, width=3.5, fill="#000000")
            cvs.create_line(x, y+10, x, y+24, width=2.5, fill="#000000")
            if label:
                cvs.create_text(x+20, y, text=label, font=("Helvetica", 10, "bold"), fill="#000000", anchor="w")

    def draw_bjt_npn(self, cvs, x, y, label="Q1"):
        """Draws compact IEEE NPN Transistor with standard proportions"""
        # Outer circle: radius 22
        cvs.create_oval(x-22, y-22, x+22, y+22, outline="#000000", width=2.5, fill="#FFFFFF")
        # Base bar
        cvs.create_line(x-8, y-14, x-8, y+14, width=4, fill="#000000")
        # Base input lead
        cvs.create_line(x-28, y, x-8, y, width=2.5, fill="#000000")
        # Collector slant and vertical lead
        cvs.create_line(x-8, y-6, x+12, y-18, width=2.5, fill="#000000")
        cvs.create_line(x+12, y-18, x+12, y-28, width=2.5, fill="#000000")
        # Emitter slant, arrow, and vertical lead
        cvs.create_line(x-8, y+6, x+12, y+18, width=2.5, fill="#000000")
        cvs.create_polygon(x+5, y+11, x+13, y+19, x+4, y+18, fill="#000000", outline="#000000")
        cvs.create_line(x+12, y+18, x+12, y+28, width=2.5, fill="#000000")
        # Terminal labels
        cvs.create_text(x+22, y-28, text="C", font=("Helvetica", 10, "bold"), fill="#0055FF")
        cvs.create_text(x-22, y-10, text="B", font=("Helvetica", 10, "bold"), fill="#0055FF")
        cvs.create_text(x+22, y+28, text="E", font=("Helvetica", 10, "bold"), fill="#0055FF")
        if label:
            cvs.create_text(x+32, y, text=label, font=("Helvetica", 11, "bold"), fill="#000000", anchor="w")

    def draw_jfet_n(self, cvs, x, y, label="J1"):
        """Draws compact IEEE N-Channel JFET"""
        cvs.create_oval(x-22, y-22, x+22, y+22, outline="#000000", width=2.5, fill="#FFFFFF")
        cvs.create_line(x-6, y-15, x-6, y+15, width=4, fill="#000000")
        cvs.create_line(x-6, y-9, x+12, y-9, width=2.5, fill="#000000")
        cvs.create_line(x+12, y-9, x+12, y-28, width=2.5, fill="#000000")
        cvs.create_line(x-6, y+9, x+12, y+9, width=2.5, fill="#000000")
        cvs.create_line(x+12, y+9, x+12, y+28, width=2.5, fill="#000000")
        cvs.create_line(x-28, y, x-6, y, width=2.5, fill="#000000")
        cvs.create_polygon(x-16, y-5, x-6, y, x-16, y+5, fill="#000000", outline="#000000")
        cvs.create_text(x+20, y-26, text="D", font=("Helvetica", 10, "bold"), fill="#0055FF")
        cvs.create_text(x-24, y-10, text="G", font=("Helvetica", 10, "bold"), fill="#0055FF")
        cvs.create_text(x+20, y+26, text="S", font=("Helvetica", 10, "bold"), fill="#0055FF")
        if label:
            cvs.create_text(x+32, y, text=label, font=("Helvetica", 11, "bold"), fill="#000000", anchor="w")

    def draw_dmos_n(self, cvs, x, y, label="M1"):
        """Draws compact IEEE Depletion-type MOSFET"""
        cvs.create_oval(x-22, y-22, x+22, y+22, outline="#000000", width=2.5, fill="#FFFFFF")
        cvs.create_line(x-28, y, x-10, y, width=2.5, fill="#000000")
        cvs.create_line(x-10, y-14, x-10, y+14, width=3, fill="#000000")
        cvs.create_line(x-5, y-14, x-5, y+14, width=4, fill="#000000")
        cvs.create_line(x-5, y-9, x+12, y-9, width=2.5, fill="#000000")
        cvs.create_line(x+12, y-9, x+12, y-28, width=2.5, fill="#000000")
        cvs.create_line(x-5, y+9, x+12, y+9, width=2.5, fill="#000000")
        cvs.create_line(x+12, y+9, x+12, y+28, width=2.5, fill="#000000")
        cvs.create_line(x-5, y, x+5, y, width=2.5, fill="#000000")
        cvs.create_line(x+5, y, x+5, y+9, width=2.5, fill="#000000")
        cvs.create_polygon(x-2, y, x+5, y-4, x+5, y+4, fill="#000000")
        cvs.create_text(x+20, y-26, text="D", font=("Helvetica", 10, "bold"), fill="#0055FF")
        cvs.create_text(x-24, y-10, text="G", font=("Helvetica", 10, "bold"), fill="#0055FF")
        cvs.create_text(x+20, y+26, text="S", font=("Helvetica", 10, "bold"), fill="#0055FF")
        if label:
            cvs.create_text(x+32, y, text=label, font=("Helvetica", 11, "bold"), fill="#000000", anchor="w")
        
    def draw_emos_n(self, cvs, x, y, label="M1"):
        """Draws compact IEEE Enhancement-type MOSFET"""
        cvs.create_oval(x-22, y-22, x+22, y+22, outline="#000000", width=2.5, fill="#FFFFFF")
        cvs.create_line(x-28, y, x-10, y, width=2.5, fill="#000000")
        cvs.create_line(x-10, y-14, x-10, y+14, width=3, fill="#000000")
        cvs.create_line(x-5, y-14, x-5, y-7, width=4, fill="#000000")
        cvs.create_line(x-5, y-3, x-5, y+3, width=4, fill="#000000")
        cvs.create_line(x-5, y+7, x-5, y+14, width=4, fill="#000000")
        cvs.create_line(x-5, y-11, x+12, y-11, width=2.5, fill="#000000")
        cvs.create_line(x+12, y-11, x+12, y-28, width=2.5, fill="#000000")
        cvs.create_line(x-5, y+11, x+12, y+11, width=2.5, fill="#000000")
        cvs.create_line(x+12, y+11, x+12, y+28, width=2.5, fill="#000000")
        cvs.create_line(x-5, y, x+5, y, width=2.5, fill="#000000")
        cvs.create_line(x+5, y, x+5, y+11, width=2.5, fill="#000000")
        cvs.create_polygon(x-2, y, x+5, y-4, x+5, y+4, fill="#000000")
        cvs.create_text(x+20, y-26, text="D", font=("Helvetica", 10, "bold"), fill="#0055FF")
        cvs.create_text(x-24, y-10, text="G", font=("Helvetica", 10, "bold"), fill="#0055FF")
        cvs.create_text(x+20, y+28, text="S", font=("Helvetica", 10, "bold"), fill="#0055FF")
        if label:
            cvs.create_text(x+32, y, text=label, font=("Helvetica", 11, "bold"), fill="#000000", anchor="w")

    # ==================== I. DIODE CALCULATOR ====================
    def show_theory(self):
        self.clear_content()
        self.create_retro_title("I. DIODE CALCULATOR & SHOCKLEY I-V CURVE")
        self.create_toolbar(reset_cmd=self.reset_diode_calc)
        
        top_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(top_frame, text="Calculate:", font=RETRO_FONT, text_color="#000000").pack(side="left", padx=5)
        self.diode_calc_combo = ctk.CTkComboBox(
            top_frame, 
            values=["AC Resistance", "DC Resistance", "Diode Current", "Diode Voltage"], 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_diode_calc
        )
        self.diode_calc_combo.pack(side="left", padx=5)
        
        self.diode_calc_form = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        self.diode_calc_form.pack(pady=10, fill="x", padx=20)
        
        res_box = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res_box.pack(fill="x", padx=20, pady=5)
        self.lbl_theory_out = ctk.CTkLabel(res_box, text="> Result...", font=RETRO_FONT, text_color="#27C93F", justify="left")
        self.lbl_theory_out.pack(padx=10, pady=10, anchor="w")
        
        self.diode_plot_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.diode_plot_frame.pack(fill="x", padx=20, pady=10)
        
        self.update_diode_calc("AC Resistance")

    def reset_diode_calc(self):
        choice = self.diode_calc_combo.get()
        self.update_diode_calc(choice)

    def update_diode_calc(self, choice):
        for widget in self.diode_calc_form.winfo_children():
            widget.destroy()
        
        self.diode_calc_entries = {}
        
        if choice == "AC Resistance":
            inputs = [("Id (mA):", "26"), ("Is (A):", "1e-12"), ("n (ideality):", "1.0"), ("Temp T (°C):", "25")]
        elif choice == "DC Resistance":
            inputs = [("Vd (V):", "0.7"), ("Is (A):", "1e-12"), ("n (ideality):", "1.0"), ("Temp T (°C):", "25")]
        elif choice == "Diode Current":
            inputs = [("Vd (V):", "0.7"), ("Is (A):", "1e-12"), ("n (ideality):", "1.0"), ("Temp T (°C):", "25")]
        elif choice == "Diode Voltage":
            inputs = [("Id (mA):", "10"), ("Is (A):", "1e-12"), ("n (ideality):", "1.0"), ("Temp T (°C):", "25")]
            
        for i, (lbl, default) in enumerate(inputs):
            ctk.CTkLabel(self.diode_calc_form, text=lbl, font=RETRO_FONT, text_color="#000000").grid(row=i, column=0, padx=10, pady=4)
            e = ctk.CTkEntry(self.diode_calc_form, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0)
            e.grid(row=i, column=1, padx=10, pady=4)
            e.insert(0, default)
            self.diode_calc_entries[lbl] = e
            
        btn = ctk.CTkButton(
            self.diode_calc_form, 
            text="Calculate & Plot Dynamic Shockley I-V Curve", 
            font=RETRO_FONT, 
            fg_color="#27C93F", 
            text_color="#000000", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            command=lambda: self.do_diode_calc(choice)
        )
        btn.grid(row=len(inputs), column=0, columnspan=2, pady=10)
        self.do_diode_calc(choice)

    def do_diode_calc(self, choice):
        """
        =============================================================================
        DYNAMIC SHOCKLEY PN JUNCTION DIODE SOLVER & I-V CHARACTERISTIC ENGINE
        =============================================================================
        Pure Python Vectorized Formulation (MATLAB-Equivalent):
          - Thermal Voltage: Vt = (k_B * (T + 273.15)) / q ≈ 25.85 mV at 25°C.
          - Shockley Current: Id = Is * (exp(Vd / (n * Vt)) - 1)
          - Forward Knee Voltage: Vd = n * Vt * ln(Id / Is + 1)
          - DC Static Resistance: RD = Vd / Id  (secant line from origin to Q-point)
          - AC Dynamic Resistance: rd = (n * Vt) / (Id + Is)  (reciprocal of tangent slope)
        =============================================================================
        """
        try:
            k_b = 1.380649e-23
            q = 1.60217663e-19
            
            # Common diode physical parameters from user entries
            Is = float(self.diode_calc_entries["Is (A):"].get())
            n = float(self.diode_calc_entries["n (ideality):"].get())
            T_celsius = float(self.diode_calc_entries["Temp T (°C):"].get())
            
            if Is <= 0: raise ValueError("Saturation Current Is must be positive > 0 A")
            if n <= 0: raise ValueError("Ideality factor n must be positive > 0")
            
            # Calculate thermodynamic thermal voltage Vt
            Vt = (k_b * (T_celsius + 273.15)) / q
            
            # Dynamic Knee Voltage (voltage at Id = 1.0 mA)
            V_knee = float(n * Vt * math.log((1e-3 / Is) + 1.0))
            
            rac = None
            rdc = None
            
            if choice == "AC Resistance":
                Id_ma = float(self.diode_calc_entries["Id (mA):"].get())
                if Id_ma <= 0: raise ValueError("Id must be positive > 0 mA")
                Id_amp = Id_ma * 1e-3
                # % MATLAB: Vd = n * Vt * log((Id / Is) + 1); rac = (n * Vt) / (Id + Is);
                Vd = float(n * Vt * math.log((Id_amp / Is) + 1.0))
                rac = float((n * Vt) / (Id_amp + Is))
                Vd_plot = Vd
                Id_plot_ma = Id_ma
                res_txt = (
                    f"> AC Dynamic Resistance (rd = n·Vt / Id) = {rac:.2f} Ω\n"
                    f"> Operating Point: Vd = {Vd:.4f} V, Id = {Id_ma:.2f} mA\n"
                    f"> Thermal Voltage Vt = {Vt*1000:.2f} mV (at {T_celsius:.1f}°C)\n"
                    f"{matlab_manager.get_status_text()}"
                )
                
            elif choice == "DC Resistance":
                Vd = float(self.diode_calc_entries["Vd (V):"].get())
                # % MATLAB: Id = Is * (exp(Vd / (n * Vt)) - 1); rdc = Vd / Id;
                Id_amp = float(Is * (math.exp(Vd / (n * Vt)) - 1.0))
                Id_ma = Id_amp * 1000.0
                if Id_amp <= 0:
                    rdc = float('inf')
                else:
                    rdc = Vd / Id_amp
                Vd_plot = Vd
                Id_plot_ma = max(Id_ma, 0.0001)
                res_txt = (
                    f"> DC Static Resistance (RD = Vd / Id) = {rdc:.2f} Ω\n"
                    f"> Operating Point: Vd = {Vd:.4f} V, Id = {Id_ma:.4f} mA ({Id_amp:.3e} A)\n"
                    f"> Dynamic Knee Voltage = ~{V_knee:.3f} V\n"
                    f"{matlab_manager.get_status_text()}"
                )
                
            elif choice == "Diode Current":
                Vd = float(self.diode_calc_entries["Vd (V):"].get())
                # % MATLAB: Id = Is * (exp(Vd / (n * Vt)) - 1);
                Id_amp = float(Is * (math.exp(Vd / (n * Vt)) - 1.0))
                Id_ma = Id_amp * 1000.0
                Vd_plot = Vd
                Id_plot_ma = max(Id_ma, 0.0001)
                res_txt = (
                    f"> Solved Diode Current (Id) = {Id_amp:.6e} A ({Id_ma:.4f} mA)\n"
                    f"> Shockley Formula: Id = Is · [exp(Vd / n·Vt) - 1]\n"
                    f"> Dynamic Knee Voltage = ~{V_knee:.3f} V\n"
                    f"{matlab_manager.get_status_text()}"
                )
                
            elif choice == "Diode Voltage":
                Id_ma = float(self.diode_calc_entries["Id (mA):"].get())
                if Id_ma <= 0: raise ValueError("Id must be positive > 0 mA")
                Id_amp = Id_ma * 1e-3
                # % MATLAB: Vd = n * Vt * log((Id / Is) + 1);
                Vd = float(n * Vt * math.log((Id_amp / Is) + 1.0))
                Vd_plot = Vd
                Id_plot_ma = Id_ma
                res_txt = (
                    f"> Solved Diode Voltage (Vd) = {Vd:.4f} V (Calculated Knee: ~{V_knee:.3f} V)\n"
                    f"> Inverted Shockley: Vd = n·Vt · ln(Id/Is + 1)\n"
                    f"> Thermal Voltage Vt = {Vt*1000:.2f} mV (at {T_celsius:.1f}°C)\n"
                    f"{matlab_manager.get_status_text()}"
                )
                
            self.lbl_theory_out.configure(text=res_txt, text_color="#27C93F")
            self.calc_history_log += f"\n[DIODE CALCULATOR - {choice}]\n{res_txt}\nTimestamp: {datetime.datetime.now()}\n"
            
            # -------------------------------------------------------------------------
            # FULLY DYNAMIC 2D SHOCKLEY I-V CHARACTERISTIC CURVE PLOT
            # -------------------------------------------------------------------------
            for w in self.diode_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.4, 2.9), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#FFFFFF")
            
            # Dynamic Voltage Range centered on operating point and knee
            V_min = -0.3
            V_max = max(Vd_plot * 1.25, V_knee + 0.12, 0.75)
            vd_vals = np.linspace(V_min, V_max, 500)
            
            # Pure Python Vectorized Shockley Curve evaluation
            id_vals_ma = (Is * (np.exp(vd_vals / (n * Vt)) - 1.0)) * 1000.0
            
            # Dynamic Y-axis limits ensuring no flat line clipping
            I_max_plot = max(Id_plot_ma * 1.35, 25.0)
            
            # 1. Main Shockley Exponential Curve
            ax.plot(vd_vals, id_vals_ma, color="#0055FF", lw=3, label=f"Shockley Curve (Is={Is:.1e}A, n={n})")
            
            # 2. Dynamic Knee Voltage Reference Line
            ax.axvline(V_knee, color="#FFBD2E", linestyle="--", lw=1.8, label=f"Dynamic Knee (~{V_knee:.2f}V)")
            
            # 3. Coordinate Axes
            ax.axhline(0, color="#000000", lw=1)
            ax.axvline(0, color="#000000", lw=1)
            
            # 4. Exact Q-Point Marker (mathematically guaranteed to lie on curve)
            ax.plot(Vd_plot, Id_plot_ma, marker='o', markersize=9, color="#FF3333", zorder=5, label=f"Q-Point ({Vd_plot:.3f}V, {Id_plot_ma:.2f}mA)")
            
            # 5. Projection lines to axes
            ax.plot([Vd_plot, Vd_plot], [0, Id_plot_ma], color="#FF3333", linestyle=":", lw=1.5)
            ax.plot([V_min, Vd_plot], [Id_plot_ma, Id_plot_ma], color="#FF3333", linestyle=":", lw=1.5)
            
            # 6. Choice-specific Tangent or Secant Lines
            if choice == "AC Resistance" and rac is not None:
                dv = 0.04 * n
                v_tan = np.linspace(max(V_min, Vd_plot - dv), min(V_max, Vd_plot + dv), 50)
                i_tan_ma = Id_plot_ma + (1000.0 / rac) * (v_tan - Vd_plot)
                ax.plot(v_tan, i_tan_ma, color="#10B981", lw=2.5, linestyle="-", label=f"Tangent Slope (rd = {rac:.1f}Ω)")
            elif choice == "DC Resistance" and rdc is not None:
                ax.plot([0, Vd_plot], [0, Id_plot_ma], color="#8B5CF6", lw=2.5, linestyle="-", label=f"Secant Slope (RD = {rdc:.1f}Ω)")
                
            ax.set_title("Diode Shockley Dynamic I-V Characteristic Curve", fontsize=11, fontweight="bold")
            ax.set_xlabel("Diode Forward Voltage Vd (Volts)", fontsize=9, fontweight="bold")
            ax.set_ylabel("Diode Current Id (mA)", fontsize=9, fontweight="bold")
            ax.set_xlim(V_min, V_max)
            ax.set_ylim(-0.06 * I_max_plot, I_max_plot)
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(fontsize=8, loc="upper left")
            
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.diode_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_theory_out.configure(text=f"> ERR: {str(e)}", text_color="#FF5F56")

    # ==================== II. DIODE APPLICATIONS ====================
    def show_diode_apps(self):
        self.clear_content()
        self.create_retro_title("II. DIODE APPLICATIONS (RECTIFIERS, CLIPPERS, LED)")
        self.create_toolbar(reset_cmd=self.reset_diode_apps)
        
        top_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(top_frame, text="Select Circuit:", font=RETRO_FONT, text_color="#000000").pack(side="left", padx=5)
        self.diode_combo = ctk.CTkComboBox(
            top_frame, 
            values=[
                "Half-wave Rectifier", 
                "Full-wave Bridge (4 Diodes)", 
                "Positive Clipper", 
                "Negative Clipper", 
                "Positive Clamper", 
                "Negative Clamper", 
                "LED Circuit"
            ], 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_diode_app
        )
        self.diode_combo.pack(side="left", padx=5)
        
        self.diode_canvas = ctk.CTkCanvas(self.content_frame, width=560, height=250, bg="#FFF5EE", highlightthickness=4, highlightbackground="#000000")
        self.diode_canvas.pack(pady=10)
        
        self.diode_form = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        self.diode_form.pack(pady=5, fill="x", padx=20)
        
        self.diode_res_frame = ctk.CTkFrame(self.content_frame, fg_color="#000000", border_width=4, corner_radius=0)
        self.diode_res_frame.pack(fill="x", padx=20, pady=5)
        
        self.lbl_diode_out = ctk.CTkLabel(self.diode_res_frame, text="> Awaiting...", font=RETRO_FONT, text_color="#27C93F", justify="left")
        self.lbl_diode_out.pack(padx=10, pady=10, anchor="w")

        self.diode_scope_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.diode_scope_frame.pack(fill="x", padx=20, pady=10)
        
        self.update_diode_app("Half-wave Rectifier")

    def reset_diode_apps(self):
        choice = self.diode_combo.get()
        self.update_diode_app(choice)

    def update_diode_app(self, choice):
        self.diode_canvas.delete("all")
        for widget in self.diode_form.winfo_children():
            widget.destroy()

        if choice == "Half-wave Rectifier":
            # AC source at (100, 125)
            self.draw_vsource_ac(self.diode_canvas, 100, 125, label="vs(t)")
            self.diode_canvas.create_line(100, 107, 100, 50, width=2.5, fill="#000000")
            self.diode_canvas.create_line(100, 50, 226, 50, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 250, 50, orient="h", label="D1 (1N4001)")
            self.diode_canvas.create_line(274, 50, 420, 50, width=2.5, fill="#000000")
            
            # Load Resistor RL
            self.draw_res_v(self.diode_canvas, 420, 50, 420, 160, label="RL (Load)")
            self.draw_gnd(self.diode_canvas, 420, 160)
            
            # AC source bottom to ground
            self.diode_canvas.create_line(100, 143, 100, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 100, 185)
            
            # Output voltage probe
            self.diode_canvas.create_oval(446, 44, 456, 54, fill="#0055FF", outline="#000000")
            self.diode_canvas.create_text(485, 48, text="+ Vo(t)", font=("Helvetica", 12, "bold"), fill="#0055FF")
            
            self.create_diode_input("Peak Input AC Volts (Vm):", "12", 0)
            self.create_diode_input("Diode Forward Drop (VD):", "0.7", 1)
            self.create_diode_input("AC Frequency (Hz):", "60", 2)
            self.create_diode_input("Load Resistor RL (Ω):", "1000", 3)
            btn = ctk.CTkButton(self.diode_form, text="Calculate & Plot Half-wave Rectifier Waveforms", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode(choice))
            btn.grid(row=4, column=0, columnspan=2, pady=10)

        elif choice == "Full-wave Bridge (4 Diodes)":
            # 4-Diode Bridge Layout: 2 vertical arms with D1, D3 on left and D2, D4 on right
            self.draw_vsource_ac(self.diode_canvas, 80, 130, label="Vin(AC)")
            
            # Left arm (x=210): D1 top (v_up), D3 bottom (v_up)
            self.diode_canvas.create_line(210, 50, 210, 61, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 210, 85, orient="v_up", label="D1")
            self.diode_canvas.create_line(210, 109, 210, 151, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 210, 175, orient="v_up", label="D3")
            self.diode_canvas.create_line(210, 199, 210, 210, width=2.5, fill="#000000")
            
            # Right arm (x=330): D2 top (v_up), D4 bottom (v_up)
            self.diode_canvas.create_line(330, 50, 330, 61, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 330, 85, orient="v_up", label="D2")
            self.diode_canvas.create_line(330, 109, 330, 151, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 330, 175, orient="v_up", label="D4")
            self.diode_canvas.create_line(330, 199, 330, 210, width=2.5, fill="#000000")
            
            # Top rail (+): connects (210, 50) and (330, 50) to Load RL (440, 50)
            self.diode_canvas.create_line(210, 50, 440, 50, width=3.5, fill="#FF3333")
            self.diode_canvas.create_text(270, 36, text="+ Vdc Rail", font=("Helvetica", 11, "bold"), fill="#FF3333")
            
            # Bottom rail (- / GND): connects (210, 210) and (330, 210) to Load RL (440, 210)
            self.diode_canvas.create_line(210, 210, 440, 210, width=3, fill="#000000")
            self.draw_gnd(self.diode_canvas, 440, 210)
            
            # Load Resistor RL
            self.draw_res_v(self.diode_canvas, 440, 50, 440, 210, label="RL (Load)")
            self.diode_canvas.create_oval(460, 45, 470, 55, fill="#0055FF")
            self.diode_canvas.create_text(495, 50, text="+ Vo(t)", font=("Helvetica", 12, "bold"), fill="#0055FF")
            
            # AC Input 1: from AC source top (80, 112) to Left arm tap (210, 130)
            self.diode_canvas.create_line(80, 112, 140, 112, width=2.5, fill="#000000")
            self.diode_canvas.create_line(140, 112, 140, 130, width=2.5, fill="#000000")
            self.diode_canvas.create_line(140, 130, 210, 130, width=2.5, fill="#000000")
            self.diode_canvas.create_oval(206, 126, 214, 134, fill="#0055FF")
            self.diode_canvas.create_text(180, 118, text="AC 1", font=("Helvetica", 9, "bold"), fill="#0055FF")
            
            # AC Input 2: from AC source bottom (80, 148) to Right arm tap (330, 130)
            self.diode_canvas.create_line(80, 148, 140, 148, width=2.5, fill="#000000")
            self.diode_canvas.create_line(140, 148, 140, 235, width=2.5, fill="#000000")
            self.diode_canvas.create_line(140, 235, 270, 235, width=2.5, fill="#000000")
            self.diode_canvas.create_line(270, 235, 270, 130, width=2.5, fill="#000000")
            self.diode_canvas.create_line(270, 130, 330, 130, width=2.5, fill="#000000")
            self.diode_canvas.create_oval(326, 126, 334, 134, fill="#0055FF")
            self.diode_canvas.create_text(300, 118, text="AC 2", font=("Helvetica", 9, "bold"), fill="#0055FF")
            
            # Bridge badge
            self.diode_canvas.create_text(270, 185, text="[ 4-DIODE BRIDGE ]", font=("Helvetica", 10, "bold"), fill="#0055FF")
            
            self.create_diode_input("Peak Input AC Volts (Vm):", "12", 0)
            self.create_diode_input("Diode Forward Drop (VD):", "0.7", 1)
            self.create_diode_input("AC Frequency (Hz):", "60", 2)
            self.create_diode_input("Load Resistor RL (Ω):", "1000", 3)
            btn = ctk.CTkButton(self.diode_form, text="Calculate & Plot 4-Diode Bridge Waveforms", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode(choice))
            btn.grid(row=4, column=0, columnspan=2, pady=10)

        elif choice == "Positive Clipper":
            self.draw_vsource_ac(self.diode_canvas, 100, 125, label="Vi")
            self.diode_canvas.create_line(100, 107, 100, 50, width=2.5, fill="#000000")
            self.diode_canvas.create_line(100, 50, 160, 50, width=2.5, fill="#000000")
            self.draw_res_h(self.diode_canvas, 160, 50, 280, 50, label="R (1kΩ)")
            self.diode_canvas.create_line(280, 50, 440, 50, width=2.5, fill="#000000")
            
            # Diode shunt to Ground pointing DOWN
            self.diode_canvas.create_line(340, 50, 340, 96, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 340, 120, orient="v_down", label="D1 (Pos Clip)")
            self.diode_canvas.create_line(340, 144, 340, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 340, 185)
            
            self.diode_canvas.create_line(100, 143, 100, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 100, 185)
            
            self.diode_canvas.create_text(475, 50, text="+ Vo", font=("Helvetica", 12, "bold"), fill="#0055FF")
            self.diode_canvas.create_oval(440, 45, 450, 55, fill="#0055FF")
            
            self.create_diode_input("Input Peak (Vi):", "10", 0)
            self.create_diode_input("Diode Forward Drop (VD):", "0.7", 1)
            self.create_diode_input("DC Bias Voltage (Vbias):", "2.0", 2)
            self.create_diode_input("AC Frequency (Hz):", "60", 3)
            btn = ctk.CTkButton(self.diode_form, text="Calculate & Plot Positive Clipper Waveforms", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode(choice))
            btn.grid(row=4, column=0, columnspan=2, pady=10)

        elif choice == "Negative Clipper":
            self.draw_vsource_ac(self.diode_canvas, 100, 125, label="Vi")
            self.diode_canvas.create_line(100, 107, 100, 50, width=2.5, fill="#000000")
            self.diode_canvas.create_line(100, 50, 160, 50, width=2.5, fill="#000000")
            self.draw_res_h(self.diode_canvas, 160, 50, 280, 50, label="R (1kΩ)")
            self.diode_canvas.create_line(280, 50, 440, 50, width=2.5, fill="#000000")
            
            # Diode shunt to Ground pointing UP
            self.diode_canvas.create_line(340, 50, 340, 96, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 340, 120, orient="v_up", label="D1 (Neg Clip)")
            self.diode_canvas.create_line(340, 144, 340, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 340, 185)
            
            self.diode_canvas.create_line(100, 143, 100, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 100, 185)
            
            self.diode_canvas.create_text(475, 50, text="+ Vo", font=("Helvetica", 12, "bold"), fill="#0055FF")
            self.diode_canvas.create_oval(440, 45, 450, 55, fill="#0055FF")
            
            self.create_diode_input("Input Peak (Vi):", "10", 0)
            self.create_diode_input("Diode Forward Drop (VD):", "0.7", 1)
            self.create_diode_input("DC Bias Voltage (Vbias):", "-2.0", 2)
            self.create_diode_input("AC Frequency (Hz):", "60", 3)
            btn = ctk.CTkButton(self.diode_form, text="Calculate & Plot Negative Clipper Waveforms", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode(choice))
            btn.grid(row=4, column=0, columnspan=2, pady=10)

        elif choice == "Positive Clamper":
            self.draw_vsource_ac(self.diode_canvas, 100, 125, label="Vi")
            self.diode_canvas.create_line(100, 107, 100, 50, width=2.5, fill="#000000")
            self.draw_cap_h(self.diode_canvas, 100, 50, 240, label="C (10µF)")
            self.diode_canvas.create_line(240, 50, 440, 50, width=2.5, fill="#000000")
            
            # Diode pointing UP (Cathode top, Anode GND) -> Shifts waveform UP
            self.diode_canvas.create_line(320, 50, 320, 96, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 320, 120, orient="v_up", label="D (Pos Clamp)")
            self.diode_canvas.create_line(320, 144, 320, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 320, 185)
            
            self.draw_res_v(self.diode_canvas, 420, 50, 420, 160, label="RL")
            self.draw_gnd(self.diode_canvas, 420, 160)
            
            self.diode_canvas.create_line(100, 143, 100, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 100, 185)
            self.diode_canvas.create_text(475, 50, text="+ Vo", font=("Helvetica", 12, "bold"), fill="#0055FF")
            
            self.create_diode_input("Input Peak (Vi):", "10", 0)
            self.create_diode_input("Diode Forward Drop (VD):", "0.7", 1)
            self.create_diode_input("DC Bias Voltage (Vbias):", "0.0", 2)
            self.create_diode_input("AC Frequency (Hz):", "60", 3)
            btn = ctk.CTkButton(self.diode_form, text="Calculate & Plot Positive Clamper Waveforms", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode(choice))
            btn.grid(row=4, column=0, columnspan=2, pady=10)

        elif choice == "Negative Clamper":
            self.draw_vsource_ac(self.diode_canvas, 100, 125, label="Vi")
            self.diode_canvas.create_line(100, 107, 100, 50, width=2.5, fill="#000000")
            self.draw_cap_h(self.diode_canvas, 100, 50, 240, label="C (10µF)")
            self.diode_canvas.create_line(240, 50, 440, 50, width=2.5, fill="#000000")
            
            # Diode pointing DOWN (Anode top, Cathode GND) -> Shifts waveform DOWN
            self.diode_canvas.create_line(320, 50, 320, 96, width=2.5, fill="#000000")
            self.draw_diode_sym(self.diode_canvas, 320, 120, orient="v_down", label="D (Neg Clamp)")
            self.diode_canvas.create_line(320, 144, 320, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 320, 185)
            
            self.draw_res_v(self.diode_canvas, 420, 50, 420, 160, label="RL")
            self.draw_gnd(self.diode_canvas, 420, 160)
            
            self.diode_canvas.create_line(100, 143, 100, 185, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 100, 185)
            self.diode_canvas.create_text(475, 50, text="+ Vo", font=("Helvetica", 12, "bold"), fill="#0055FF")
            
            self.create_diode_input("Input Peak (Vi):", "10", 0)
            self.create_diode_input("Diode Forward Drop (VD):", "0.7", 1)
            self.create_diode_input("DC Bias Voltage (Vbias):", "0.0", 2)
            self.create_diode_input("AC Frequency (Hz):", "60", 3)
            btn = ctk.CTkButton(self.diode_form, text="Calculate & Plot Negative Clamper Waveforms", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode(choice))
            btn.grid(row=4, column=0, columnspan=2, pady=10)

        elif choice == "LED Circuit":
            self.diode_canvas.create_text(80, 45, text="+ Vcc", font=("Helvetica", 14, "bold"), fill="#FF3333")
            self.diode_canvas.create_oval(75, 56, 85, 66, fill="#FF3333")
            self.diode_canvas.create_line(80, 66, 80, 100, width=2.5, fill="#000000")
            self.diode_canvas.create_line(80, 100, 140, 100, width=2.5, fill="#000000")
            
            self.draw_res_h(self.diode_canvas, 140, 100, 270, 100, label="R_lim")
            self.diode_canvas.create_line(270, 100, 316, 100, width=2.5, fill="#000000")
            
            self.draw_diode_sym(self.diode_canvas, 340, 100, orient="h", label="LED")
            self.diode_canvas.create_line(340, 76, 355, 60, width=2.5, fill="#FFBD2E")
            self.diode_canvas.create_line(350, 74, 365, 58, width=2.5, fill="#FFBD2E")
            
            self.diode_canvas.create_line(364, 100, 450, 100, width=2.5, fill="#000000")
            self.diode_canvas.create_line(450, 100, 450, 160, width=2.5, fill="#000000")
            self.draw_gnd(self.diode_canvas, 450, 160)
            
            self.create_diode_input("Vcc (V):", "5", 0)
            self.create_diode_input("Vf (LED Drop):", "2.0", 1)
            self.create_diode_input("Id (Desired mA):", "15", 2)
            btn = ctk.CTkButton(self.diode_form, text="Calculate Series Resistor & LED Operating Line", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode(choice))
            btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.calc_diode(choice)

    def create_diode_input(self, label, default, row=0):
        if not hasattr(self, 'diode_entries'):
            self.diode_entries = {}
        if row == 0:
            self.diode_entries.clear()
        ctk.CTkLabel(self.diode_form, text=label, font=RETRO_FONT, text_color="#000000").grid(row=row, column=0, padx=10, pady=4)
        entry = ctk.CTkEntry(self.diode_form, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0)
        entry.grid(row=row, column=1, padx=10, pady=4)
        entry.insert(0, default)
        self.diode_entries[label] = entry

    def calc_diode(self, choice):
        """
        =============================================================================
        DIODE APPLICATIONS COMPUTATION & DYNAMIC OSCILLOSCOPE WAVEFORM ENGINE
        =============================================================================
        Solves fundamental non-linear diode wave-shaping and power-conversion circuits
        in 100% Pure Python using vectorized NumPy formulations (MATLAB-Equivalent):
        
        1. Half-Wave Rectifier:
           - Vout(t) = max(0, Vin(t) - Vd)
           - Vdc = (Vm - Vd) / π, Vrms = (Vm - Vd) / 2
        2. Full-Wave Bridge Rectifier (4 Diodes):
           - Vout(t) = max(0, |Vin(t)| - 2*Vd)
           - Vdc = 2*(Vm - 2*Vd) / π, Vrms = (Vm - 2*Vd) / √2
        3. Positive Clipper:
           - Vout(t) = min(Vin(t), Vbias + Vd)
        4. Negative Clipper:
           - Vout(t) = max(Vin(t), Vbias - Vd)
        5. Positive Clamper:
           - Vout(t) = Vin(t) + (Vm - Vd + Vbias)
        6. Negative Clamper:
           - Vout(t) = Vin(t) - (Vm - Vd - Vbias)
        7. LED Resistor Limiter:
           - R_lim = (Vcc - Vf) / Id
        =============================================================================
        """
        try:
            # Common parameters extraction
            if choice in ["Half-wave Rectifier", "Full-wave Bridge (4 Diodes)"]:
                Vm = float(self.diode_entries["Peak Input AC Volts (Vm):"].get())
                Vd = float(self.diode_entries["Diode Forward Drop (VD):"].get())
                f = float(self.diode_entries["AC Frequency (Hz):"].get())
                RL = float(self.diode_entries["Load Resistor RL (Ω):"].get())
                if f <= 0: raise ValueError("Frequency f must be positive > 0 Hz")
                if RL <= 0: raise ValueError("Load Resistor RL must be > 0 Ω")
                
                T_period = 1.0 / f
                t = np.linspace(0, 2.0 * T_period, 600)
                omega = 2.0 * np.pi * f
                vin = Vm * np.sin(omega * t)
                Vclip = None
                Vclamp_bound = None
                
                if choice == "Half-wave Rectifier":
                    # % MATLAB: vout = max(0, vin - Vd); Vout_pk = max(0, Vm - Vd);
                    vout = np.maximum(0.0, vin - Vd)
                    Vout_pk = max(0.0, Vm - Vd)
                    Vdc = Vout_pk / np.pi
                    Vrms = Vout_pk / 2.0
                    PIV = Vm
                    Ipeak = (Vout_pk / RL) * 1000.0  # mA
                    out_txt = (
                        f"> Peak Output (Vo_pk = Vm - VD) = {Vout_pk:.2f} V\n"
                        f"> DC Average Output (Vdc = Vo_pk/π) = {Vdc:.2f} V\n"
                        f"> RMS Output Voltage (Vrms = Vo_pk/2) = {Vrms:.2f} V\n"
                        f"> Peak Inverse Voltage (PIV) = {PIV:.2f} V | Peak Current = {Ipeak:.2f} mA\n"
                        f"{matlab_manager.get_status_text()}"
                    )
                else:  # Full-wave Bridge (4 Diodes)
                    # % MATLAB: vout = max(0, abs(vin) - 2*Vd); Vout_pk = max(0, Vm - 2*Vd);
                    vout = np.maximum(0.0, np.abs(vin) - 2.0 * Vd)
                    Vout_pk = max(0.0, Vm - 2.0 * Vd)
                    Vdc = (2.0 * Vout_pk) / np.pi
                    Vrms = Vout_pk / np.sqrt(2.0)
                    PIV = Vm - Vd
                    Ipeak = (Vout_pk / RL) * 1000.0  # mA
                    out_txt = (
                        f"> Peak Output (Vo_pk = Vm - 2·VD) = {Vout_pk:.2f} V\n"
                        f"> DC Average Output (Vdc = 2·Vo_pk/π) = {Vdc:.2f} V\n"
                        f"> RMS Output Voltage (Vrms = Vo_pk/√2) = {Vrms:.2f} V\n"
                        f"> Diode PIV = {PIV:.2f} V | Peak Current = {Ipeak:.2f} mA\n"
                        f"{matlab_manager.get_status_text()}"
                    )

            elif choice in ["Positive Clipper", "Negative Clipper"]:
                Vi = float(self.diode_entries["Input Peak (Vi):"].get())
                Vd = float(self.diode_entries["Diode Forward Drop (VD):"].get())
                Vbias = float(self.diode_entries["DC Bias Voltage (Vbias):"].get())
                f = float(self.diode_entries["AC Frequency (Hz):"].get())
                if f <= 0: raise ValueError("Frequency f must be positive > 0 Hz")
                
                T_period = 1.0 / f
                t = np.linspace(0, 2.0 * T_period, 600)
                omega = 2.0 * np.pi * f
                vin = Vi * np.sin(omega * t)
                Vclamp_bound = None
                
                if choice == "Positive Clipper":
                    # % MATLAB: Vclip = Vbias + Vd; vout = min(vin, Vclip);
                    Vclip = Vbias + Vd
                    vout = np.minimum(vin, Vclip)
                    Vdc = float(np.mean(vout))
                    out_txt = (
                        f"> Positive Clipping Threshold (Vclip = Vbias + VD) = {Vclip:.2f} V\n"
                        f"> Maximum Output Level = {Vclip:.2f} V | Negative Swing Preserved = -{Vi:.2f} V\n"
                        f"> DC Average Level (Vdc) = {Vdc:.2f} V\n"
                        f"> Peak-to-Peak Output Swing = {Vclip + Vi:.2f} V\n"
                        f"{matlab_manager.get_status_text()}"
                    )
                else:  # Negative Clipper
                    # % MATLAB: Vclip = Vbias - Vd; vout = max(vin, Vclip);
                    Vclip = Vbias - Vd
                    vout = np.maximum(vin, Vclip)
                    Vdc = float(np.mean(vout))
                    out_txt = (
                        f"> Negative Clipping Threshold (Vclip = Vbias - VD) = {Vclip:.2f} V\n"
                        f"> Minimum Output Level = {Vclip:.2f} V | Positive Swing Preserved = +{Vi:.2f} V\n"
                        f"> DC Average Level (Vdc) = {Vdc:.2f} V\n"
                        f"> Peak-to-Peak Output Swing = {Vi - Vclip:.2f} V\n"
                        f"{matlab_manager.get_status_text()}"
                    )

            elif choice in ["Positive Clamper", "Negative Clamper"]:
                Vi = float(self.diode_entries["Input Peak (Vi):"].get())
                Vd = float(self.diode_entries["Diode Forward Drop (VD):"].get())
                Vbias = float(self.diode_entries["DC Bias Voltage (Vbias):"].get())
                f = float(self.diode_entries["AC Frequency (Hz):"].get())
                if f <= 0: raise ValueError("Frequency f must be positive > 0 Hz")
                
                T_period = 1.0 / f
                t = np.linspace(0, 2.0 * T_period, 600)
                omega = 2.0 * np.pi * f
                vin = Vi * np.sin(omega * t)
                Vclip = None
                
                if choice == "Positive Clamper":
                    # Shifts waveform UP so negative peak clamps to Vbias - Vd
                    # % MATLAB: Vshift = Vi - Vd + Vbias; vout = vin + Vshift;
                    Vshift = Vi - Vd + Vbias
                    vout = vin + Vshift
                    Vclamp_bound = Vbias - Vd
                    Vmax = 2.0 * Vi - Vd + Vbias
                    Vdc = float(np.mean(vout))
                    out_txt = (
                        f"> Positive Clamping Shift (Vshift) = +{Vshift:.2f} V (Shifted UP)\n"
                        f"> Minimum Clamped Base = {Vclamp_bound:.2f} V (Vbias - VD)\n"
                        f"> Maximum Output Peak = {Vmax:.2f} V\n"
                        f"> Peak-to-Peak Swing Preserved = {2.0*Vi:.2f} V | Vdc = {Vdc:.2f} V\n"
                        f"{matlab_manager.get_status_text()}"
                    )
                else:  # Negative Clamper
                    # Shifts waveform DOWN so positive peak clamps to Vbias + Vd
                    # % MATLAB: Vshift = -(Vi - Vd - Vbias); vout = vin + Vshift;
                    Vshift = -(Vi - Vd - Vbias)
                    vout = vin + Vshift
                    Vclamp_bound = Vbias + Vd
                    Vmin = -(2.0 * Vi - Vd - Vbias)
                    Vdc = float(np.mean(vout))
                    out_txt = (
                        f"> Negative Clamping Shift (Vshift) = {Vshift:.2f} V (Shifted DOWN)\n"
                        f"> Maximum Clamped Peak = {Vclamp_bound:.2f} V (Vbias + VD)\n"
                        f"> Minimum Output Base = {Vmin:.2f} V\n"
                        f"> Peak-to-Peak Swing Preserved = {2.0*Vi:.2f} V | Vdc = {Vdc:.2f} V\n"
                        f"{matlab_manager.get_status_text()}"
                    )

            elif choice == "LED Circuit":
                Vcc = float(self.diode_entries["Vcc (V):"].get())
                Vf = float(self.diode_entries["Vf (LED Drop):"].get())
                Id_ma = float(self.diode_entries["Id (Desired mA):"].get())
                if Vcc <= Vf: raise ValueError("Supply Vcc must be strictly greater than LED forward voltage Vf")
                if Id_ma <= 0: raise ValueError("LED current must be positive > 0 mA")
                
                # Ohm's law current-limiting series resistance
                # % MATLAB: R_lim = (Vcc - Vf) / (Id_ma * 1e-3);
                Id_amp = Id_ma * 1e-3
                R_lim = (Vcc - Vf) / Id_amp
                P_r_mw = (Id_amp**2) * R_lim * 1000.0
                P_led_mw = Vf * Id_ma
                out_txt = (
                    f"> Required Current-Limiting Resistor (R_lim) = {R_lim:.2f} Ω\n"
                    f"> Resistor Power Dissipation = {P_r_mw:.1f} mW\n"
                    f"> LED Operating Power = {P_led_mw:.1f} mW at {Id_ma:.1f} mA\n"
                    f"{matlab_manager.get_status_text()}"
                )
                vin = None
                vout = None
                
            self.lbl_diode_out.configure(text=out_txt, text_color="#27C93F")
            self.calc_history_log += f"\n[DIODE APPLICATION - {choice}]\n{out_txt}\nTimestamp: {datetime.datetime.now()}\n"
            
            # -------------------------------------------------------------------------
            # DYNAMIC OSCILLOSCOPE TIME-DOMAIN / LOAD LINE PLOT
            # -------------------------------------------------------------------------
            for w in self.diode_scope_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.4, 3.0), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            ax = fig.add_subplot(111)
            
            if choice != "LED Circuit":
                # Dark Digital Oscilloscope CRT Screen
                ax.set_facecolor("#0F172A")
                t_ms = t * 1000.0
                
                # 1. Input Trace CH1 (Neon Cyan Dashed)
                ax.plot(t_ms, vin, color="#38BDF8", lw=2.0, linestyle="--", label="CH1: Vin(t)")
                
                # 2. Output Trace CH2 (Neon Lime Solid)
                ax.plot(t_ms, vout, color="#4ADE80", lw=3.0, label="CH2: Vout(t)")
                
                # 3. DC Average Reference Line (Amber Dotted)
                ax.axhline(Vdc, color="#F59E0B", linestyle=":", lw=2.0, label=f"Vdc Mean ({Vdc:.2f}V)")
                
                # 4. Zero Ground Line
                ax.axhline(0, color="#64748B", lw=1.2)
                
                # 5. Specialized Threshold Markers
                if Vclip is not None:
                    ax.axhline(Vclip, color="#EF4444", linestyle="-.", lw=1.8, label=f"Vclip ({Vclip:.2f}V)")
                if Vclamp_bound is not None:
                    ax.axhline(Vclamp_bound, color="#EC4899", linestyle="-.", lw=1.8, label=f"Clamp Bound ({Vclamp_bound:.2f}V)")
                    
                # Dynamic Headroom scaling
                y_low = min(float(np.min(vin)), float(np.min(vout)))
                y_high = max(float(np.max(vin)), float(np.max(vout)))
                span = max(y_high - y_low, 1.0)
                ax.set_ylim(y_low - 0.22 * span, y_high + 0.26 * span)
                ax.set_xlim(0, 2.0 * T_period * 1000.0)
                
                ax.set_title(f"Dynamic Oscilloscope Display (2 Cycles at {f:.0f} Hz) - {choice}", fontsize=11, fontweight="bold", color="#000000")
                ax.set_xlabel("Time (milliseconds)", fontsize=9, fontweight="bold")
                ax.set_ylabel("Voltage (Volts)", fontsize=9, fontweight="bold")
                ax.grid(True, linestyle=":", alpha=0.35, color="#94A3B8")
                ax.legend(fontsize=8, loc="upper right", facecolor="#1E293B", edgecolor="#475569", labelcolor="#FFFFFF")
                
            else:
                # LED DC Load Line & Exponential Forward Characteristic
                ax.set_facecolor("#FFFFFF")
                v_axis = np.linspace(0, Vcc * 1.25, 300)
                i_load = np.maximum(0.0, (Vcc - v_axis) / (R_lim / 1000.0))  # mA
                
                # Simulated LED exponential curve through (Vf, Id_ma)
                # I = Id * exp((V - Vf) / 0.1)
                i_led = Id_ma * np.exp(np.clip((v_axis - Vf) / 0.15, -10, 8))
                
                ax.plot(v_axis, i_load, color="#EF4444", lw=3, label="DC Load Line: I = (Vcc - V) / R")
                ax.plot(v_axis, i_led, color="#0055FF", lw=2.5, linestyle="--", label="LED Exponential I-V Characteristic")
                ax.plot(Vf, Id_ma, marker='o', markersize=9, color="#27C93F", zorder=5, label=f"Operating Q-Point ({Vf:.2f}V, {Id_ma:.1f}mA)")
                
                ax.set_title("LED Graphical DC Load Line & Operating Point", fontsize=11, fontweight="bold")
                ax.set_xlabel("LED Forward Voltage (Volts)", fontsize=9, fontweight="bold")
                ax.set_ylabel("Current (mA)", fontsize=9, fontweight="bold")
                ax.set_xlim(0, Vcc * 1.15)
                ax.set_ylim(0, max(Id_ma * 2.0, (Vcc / (R_lim / 1000.0)) * 1.1))
                ax.grid(True, linestyle=":", alpha=0.6)
                ax.legend(fontsize=8, loc="upper right")
                
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.diode_scope_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_diode_out.configure(text=f"> ERR: {str(e)}", text_color="#FF5F56")

    # ==================== III. BJT FUNDAMENTALS ====================
    def show_bjt(self):
        self.clear_content()
        self.create_retro_title("III. BJT FUNDAMENTALS (DC EQUATIONS & RATIOS)")
        self.create_toolbar(reset_cmd=self.reset_bjt)
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        top = ctk.CTkFrame(box, fg_color="transparent")
        top.pack(pady=5)
        
        ctk.CTkLabel(top, text="Solve For Parameter:", font=RETRO_FONT, text_color="#000000").pack(side="left", padx=5)
        self.bjt_param_combo = ctk.CTkComboBox(
            top, 
            values=["Rb", "Rc", "Re", "Ic", "Ie", "Ib", "Beta", "VCC", "VEE", "VCE", "Isat"], 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_bjt_fund_wrapper
        )
        self.bjt_param_combo.pack(side="left", padx=5)

        ctk.CTkLabel(top, text="Bias Type:", font=RETRO_FONT, text_color="#000000").pack(side="left", padx=5)
        self.bjt_bias_combo = ctk.CTkComboBox(
            top, 
            values=["Fixed Bias", "Emitter Bias"], 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_bjt_fund_wrapper
        )
        self.bjt_bias_combo.pack(side="left", padx=5)
        
        self.bjt_fund_form = ctk.CTkFrame(box, fg_color="transparent")
        self.bjt_fund_form.pack(pady=5)
        
        res_frame = ctk.CTkFrame(box, fg_color="#000000", corner_radius=0)
        res_frame.pack(fill="x", padx=20, pady=10)
        self.lbl_bjt_fund = ctk.CTkLabel(res_frame, text="> Results...", font=RETRO_FONT, text_color="#27C93F", justify="left")
        self.lbl_bjt_fund.pack(padx=10, pady=10, anchor="w")

        self.bjt_plot_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.bjt_plot_frame.pack(fill="x", padx=20, pady=10)
        
        self.update_bjt_fund("Isat (Fixed Bias)")

    def update_bjt_fund_wrapper(self, _=None):
        param = self.bjt_param_combo.get()
        bias = self.bjt_bias_combo.get()
        
        # Determine the logical choice based on combinations
        if param in ["Ic", "Ie", "Beta", "VEE"]:
            choice = param
        elif param == "Re":
            choice = "Re (Emitter Bias)"
        else:
            choice = f"{param} ({bias})"
            
        self.update_bjt_fund(choice)

    def reset_bjt(self):
        self.update_bjt_fund_wrapper()

    def update_bjt_fund(self, choice):
        for w in self.bjt_fund_form.winfo_children(): w.destroy()
        self.bjt_fund_entries = {}
        
        if choice == "Rb (Fixed Bias)": inputs = [("VCC (V)", "12"), ("VBE (V)", "0.7"), ("Ib (µA)", "40")]
        elif choice == "Rb (Emitter Bias)": inputs = [("VCC (V)", "12"), ("VBE (V)", "0.7"), ("Ib (µA)", "40"), ("Beta", "100"), ("Re (kΩ)", "1.2")]
        elif choice == "Rc (Fixed Bias)": inputs = [("VCC (V)", "12"), ("VCE (V)", "6"), ("Ic (mA)", "3")]
        elif choice == "Rc (Emitter Bias)": inputs = [("VCC (V)", "12"), ("VCE (V)", "6"), ("Ic (mA)", "3"), ("Re (kΩ)", "1.2")]
        elif choice == "Re (Emitter Bias)": inputs = [("VEE (V)", "5"), ("VBE (V)", "0.7"), ("Ie (mA)", "2.5")]
        elif choice == "Ic": inputs = [("Beta", "100"), ("Ib (µA)", "25")]
        elif choice == "Ie": inputs = [("Ic (mA)", "5"), ("Ib (µA)", "50")]
        elif choice == "Ib (Fixed Bias)": inputs = [("VCC (V)", "12"), ("VBE (V)", "0.7"), ("Rb (kΩ)", "240")]
        elif choice == "Ib (Emitter Bias)": inputs = [("VCC (V)", "12"), ("VBE (V)", "0.7"), ("Rb (kΩ)", "240"), ("Beta", "100"), ("Re (kΩ)", "1.2")]
        elif choice == "Beta": inputs = [("Ic (mA)", "10"), ("Ib (µA)", "100")]
        elif choice == "VCC (Fixed Bias)": inputs = [("Ic (mA)", "4"), ("Rc (kΩ)", "2.2"), ("VCE (V)", "6")]
        elif choice == "VCC (Emitter Bias)": inputs = [("Ic (mA)", "4"), ("Rc (kΩ)", "2.2"), ("Re (kΩ)", "1.2"), ("VCE (V)", "6")]
        elif choice == "VEE": inputs = [("Ie (mA)", "3"), ("Re (kΩ)", "1.5"), ("VBE (V)", "0.7")]
        elif choice == "VCE (Fixed Bias)": inputs = [("VCC (V)", "12"), ("Ic (mA)", "2"), ("Rc (kΩ)", "2")]
        elif choice == "VCE (Emitter Bias)": inputs = [("VCC (V)", "12"), ("Ic (mA)", "2"), ("Rc (kΩ)", "2"), ("Re (kΩ)", "1")]
        elif choice == "Isat (Fixed Bias)": inputs = [("VCC (V)", "12"), ("Rc (kΩ)", "2.2")]
        elif choice == "Isat (Emitter Bias)": inputs = [("VCC (V)", "12"), ("Rc (kΩ)", "2.2"), ("Re (kΩ)", "0.5")]
        else: inputs = [("VCC (V)", "12"), ("Rc (kΩ)", "2.2")]
        
        for i, (lbl, default) in enumerate(inputs):
            ctk.CTkLabel(self.bjt_fund_form, text=lbl+":", font=RETRO_FONT, text_color="#000000").grid(row=i, column=0, padx=5, pady=2, sticky="e")
            e = ctk.CTkEntry(self.bjt_fund_form, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0)
            e.grid(row=i, column=1, pady=2)
            e.insert(0, default)
            self.bjt_fund_entries[lbl] = e
            
        btn = ctk.CTkButton(self.bjt_fund_form, text="Calculate & Plot Transfer Relation", font=RETRO_FONT, fg_color="#4CA8D1", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_bjt_fund(choice))
        btn.grid(row=len(inputs), column=0, columnspan=2, pady=10)
        self.calc_bjt_fund(choice)

    def calc_bjt_fund(self, choice):
        """
        =============================================================================
        BJT FUNDAMENTALS & OPERATING CHARACTERISTIC EQUATIONS
        =============================================================================
        Evaluates Bipolar Junction Transistor active region terminal equations:
        
        1. Base Current & Resistance:
           - Vcc = Ib * Rb + Vbe  =>  Rb = (Vcc - Vbe) / Ib
           
        2. Collector Current & Resistance:
           - Vce = Vcc - Ic * Rc  =>  Rc = (Vcc - Vce) / Ic
           
        3. Emitter Resistance:
           - Re = (|Vee| - Vbe) / Ie
           
        4. Current Amplification (Beta / hFE):
           - Ic = β * Ib  =>  β = Ic / Ib
           
        5. Emitter Current (Kirchhoff's Node Equation):
           - Ie = Ic + Ib = (β + 1) * Ib
           
        6. Saturation Collector Current:
           - Icsat = Vcc / (Rc + Re)
        =============================================================================
        """
        try:
            v = {k: float(e.get()) for k, e in self.bjt_fund_entries.items()}
            res = 0
            
            # Check for native MATLAB Engine evaluation
            if matlab_manager.is_connected:
                m_res = matlab_manager.eval_matlab("semiconductor_calc", "bjt_fund", choice, v)
                if m_res and "result" in m_res:
                    res = float(m_res["result"])
                else:
                    m_res = None
            else:
                m_res = None

            if m_res is None:
                # Built-in high-precision Python math fallback
                if choice == "Rb (Fixed Bias)": res = (v["VCC (V)"] - v["VBE (V)"]) / (v["Ib (µA)"] * 1e-6) / 1000
                elif choice == "Rb (Emitter Bias)": res = ((v["VCC (V)"] - v["VBE (V)"]) / (v["Ib (µA)"] * 1e-6) - (v["Beta"] + 1) * (v["Re (kΩ)"] * 1000)) / 1000
                elif choice == "Rc (Fixed Bias)": res = (v["VCC (V)"] - v["VCE (V)"]) / (v["Ic (mA)"] * 1e-3) / 1000
                elif choice == "Rc (Emitter Bias)": res = ((v["VCC (V)"] - v["VCE (V)"]) / (v["Ic (mA)"] * 1e-3) - v["Re (kΩ)"] * 1000) / 1000
                elif choice == "Re (Emitter Bias)": res = (abs(v["VEE (V)"]) - v["VBE (V)"]) / (v["Ie (mA)"] * 1e-3) / 1000
                elif choice == "Ic": res = v["Beta"] * (v["Ib (µA)"] * 1e-3)
                elif choice == "Ie": res = v["Ic (mA)"] + (v["Ib (µA)"] * 1e-3)
                elif choice == "Ib (Fixed Bias)": res = (v["VCC (V)"] - v["VBE (V)"]) / (v["Rb (kΩ)"] * 1000) * 1e6
                elif choice == "Ib (Emitter Bias)": res = (v["VCC (V)"] - v["VBE (V)"]) / (v["Rb (kΩ)"] * 1000 + (v["Beta"] + 1) * v["Re (kΩ)"] * 1000) * 1e6
                elif choice == "Beta": res = v["Ic (mA)"] / (v["Ib (µA)"] * 1e-3)
                elif choice == "VCC (Fixed Bias)": res = v["VCE (V)"] + (v["Ic (mA)"] * 1e-3) * (v["Rc (kΩ)"] * 1000)
                elif choice == "VCC (Emitter Bias)": res = v["VCE (V)"] + (v["Ic (mA)"] * 1e-3) * ((v["Rc (kΩ)"] + v["Re (kΩ)"]) * 1000)
                elif choice == "VEE": res = -((v["Ie (mA)"] * 1e-3) * (v["Re (kΩ)"] * 1000) + v["VBE (V)"])
                elif choice == "VCE (Fixed Bias)": res = v["VCC (V)"] - (v["Ic (mA)"] * 1e-3) * (v["Rc (kΩ)"] * 1000)
                elif choice == "VCE (Emitter Bias)": res = v["VCC (V)"] - (v["Ic (mA)"] * 1e-3) * ((v["Rc (kΩ)"] + v["Re (kΩ)"]) * 1000)
                elif choice == "Isat (Fixed Bias)": res = v["VCC (V)"] / (v["Rc (kΩ)"] * 1000) * 1000
                elif choice == "Isat (Emitter Bias)": res = v["VCC (V)"] / ((v["Rc (kΩ)"] + v["Re (kΩ)"]) * 1000) * 1000
                else: res = 0
                
            units = {"Rb": "kΩ", "Rc": "kΩ", "Re": "kΩ", "Ic": "mA", "Ie": "mA", "Ib": "µA", "Beta": "", "VCC": "V", "VEE": "V", "VCE": "V", "Isat": "mA"}
            base_param = choice.split(" ")[0]
            
            res_txt = f"> Solved Parameter: {choice} = {res:.4f} {units.get(base_param, '')}\n> Active Region Model: Ic = β·Ib, Ie = Ic + Ib, Vbe = 0.7V"
            self.lbl_bjt_fund.configure(text=res_txt, text_color="#27C93F")
            self.calc_history_log += f"\n[BJT FUNDAMENTALS - {choice}]\n{res_txt}\nTimestamp: {datetime.datetime.now()}\n"
            
            # Dynamic 2D Plot: Ic vs Ib Transfer Curve
            for w in self.bjt_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.0, 2.5), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#FFFFFF")
            
            beta_val = v.get("Beta", 100)
            ib_arr = np.linspace(0, 100, 200) # µA
            ic_arr = beta_val * ib_arr * 1e-3 # mA
            ax.plot(ib_arr, ic_arr, color="#0055FF", lw=3, label=f"Ic = β·Ib (β={beta_val:.0f})")
            
            ib_pt = v.get("Ib (µA)", 40)
            ic_pt = beta_val * ib_pt * 1e-3
            ax.plot(ib_pt, ic_pt, marker='o', markersize=9, color="#FF3333", label=f"Operating Point ({ib_pt:.1f}µA, {ic_pt:.2f}mA)")
            
            ax.set_title("BJT Base-to-Collector Linear Transfer Curve", fontsize=11, fontweight="bold")
            ax.set_xlabel("Base Current Ib (µA)", fontsize=9, fontweight="bold")
            ax.set_ylabel("Collector Current Ic (mA)", fontsize=9, fontweight="bold")
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(fontsize=8, loc="upper left")
            
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.bjt_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_bjt_fund.configure(text=f"> Error: {e}", text_color="#FF5F56")

    # ==================== IV. BJT DC BIASING ====================
    def show_bjt_dc(self):
        self.clear_content()
        self.create_retro_title("IV. BJT DC BIASING & DC LOAD LINE")
        self.create_toolbar(reset_cmd=self.reset_bjt_dc)
        
        top_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(top_frame, text="Bias Circuit:", font=RETRO_FONT, text_color="#000000").pack(side="left", padx=5)
        self.bjt_bias_combo = ctk.CTkComboBox(
            top_frame, 
            values=["Fixed Bias", "Voltage Divider", "Emitter Bias", "Collector Feedback"], 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_bjt_bias
        )
        self.bjt_bias_combo.pack(side="left", padx=5)
        
        self.bias_cvs = ctk.CTkCanvas(self.content_frame, width=560, height=300, bg="#FFF5EE", highlightthickness=4, highlightbackground="#000000")
        self.bias_cvs.pack(pady=10)
        
        self.bias_form = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        self.bias_form.pack(pady=5, fill="x", padx=20)
        
        res_frame = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res_frame.pack(fill="x", padx=20, pady=5)
        self.lbl_bias_out = ctk.CTkLabel(res_frame, text="> Awaiting Calculation...", font=RETRO_FONT, text_color="#27C93F", justify="left")
        self.lbl_bias_out.pack(padx=10, pady=10, anchor="w")

        self.bias_plot_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.bias_plot_frame.pack(fill="x", padx=20, pady=10)
        
        self.update_bjt_bias("Fixed Bias")

    def reset_bjt_dc(self):
        choice = self.bjt_bias_combo.get()
        self.update_bjt_bias(choice)

    def update_bjt_bias(self, choice):
        self.bias_cvs.delete("all")
        for w in self.bias_form.winfo_children(): w.destroy()
        self.bjt_bias_entries = {}

        # Top Vcc rail across (120 to 440) at y=30
        self.bias_cvs.create_line(120, 30, 440, 30, width=4, fill="#FF3333")
        self.bias_cvs.create_text(280, 16, text="+ Vcc Power Rail", font=("Helvetica", 12, "bold"), fill="#FF3333")

        # Transistor NPN centered at (280, 150)
        # Pins: Base (252, 150), Collector (292, 122), Emitter (292, 178)
        self.draw_bjt_npn(self.bias_cvs, 280, 150, label="Q1")

        if choice == "Fixed Bias":
            # Base branch: Vcc -> Rb -> Base
            self.draw_res_v(self.bias_cvs, 160, 30, 160, 150, label="Rb")
            self.bias_cvs.create_line(160, 150, 252, 150, width=2.5, fill="#000000")
            
            # Collector branch: Vcc -> Rc -> Collector
            self.draw_res_v(self.bias_cvs, 292, 30, 292, 122, label="Rc")
            
            # Emitter to ground
            self.bias_cvs.create_line(292, 178, 292, 255, width=2.5, fill="#000000")
            self.draw_gnd(self.bias_cvs, 292, 255)
            
            inputs = [("Vcc (V):", "12"), ("Rb (kΩ):", "240"), ("Rc (kΩ):", "2.2"), ("Beta:", "50")]

        elif choice == "Voltage Divider":
            # R1 top: Vcc to node (160, 150)
            self.draw_res_v(self.bias_cvs, 160, 30, 160, 150, label="R1")
            self.bias_cvs.create_oval(157, 147, 163, 153, fill="#000000") # Node dot
            
            # R2 bottom: node (160, 150) to ground
            self.draw_res_v(self.bias_cvs, 160, 150, 160, 245, label="R2")
            self.draw_gnd(self.bias_cvs, 160, 245)
            
            # Node to Base pin
            self.bias_cvs.create_line(160, 150, 252, 150, width=2.5, fill="#000000")
            
            # Collector branch: Vcc -> Rc -> Collector
            self.draw_res_v(self.bias_cvs, 292, 30, 292, 122, label="Rc")
            
            # Emitter resistor Re to ground
            self.draw_res_v(self.bias_cvs, 292, 178, 292, 245, label="Re")
            self.draw_gnd(self.bias_cvs, 292, 245)
            
            inputs = [("Vcc (V):", "22"), ("R1 (kΩ):", "39"), ("R2 (kΩ):", "3.9"), ("Rc (kΩ):", "10"), ("Re (kΩ):", "1.5"), ("Beta:", "140")]

        elif choice == "Emitter Bias":
            # Base resistor
            self.bias_cvs.create_line(160, 50, 160, 60, width=2.5, fill="#000000")
            self.draw_gnd(self.bias_cvs, 160, 50)
            self.draw_res_v(self.bias_cvs, 160, 60, 160, 150, label="Rb")
            self.bias_cvs.create_line(160, 150, 252, 150, width=2.5, fill="#000000")
            
            # Collector branch
            self.draw_res_v(self.bias_cvs, 292, 30, 292, 122, label="Rc")
            
            # Emitter branch
            self.draw_res_v(self.bias_cvs, 292, 178, 292, 245, label="Re")
            self.draw_gnd(self.bias_cvs, 292, 245)
            
            inputs = [("Vcc (V):", "20"), ("Rb (kΩ):", "430"), ("Rc (kΩ):", "2.0"), ("Re (kΩ):", "1.0"), ("Beta:", "50")]

        elif choice == "Collector Feedback":
            # Rc from Vcc rail (y=30) to tap node (292, 80)
            self.draw_res_v(self.bias_cvs, 292, 30, 292, 80, label="Rc")
            self.bias_cvs.create_oval(289, 77, 295, 83, fill="#000000") # Tap node dot
            
            # Straight collector lead from tap node down to Collector pin (292, 122)
            self.bias_cvs.create_line(292, 80, 292, 122, width=2.5, fill="#000000")
            
            # Feedback horizontal wire to left branch
            self.bias_cvs.create_line(292, 80, 160, 80, width=2.5, fill="#000000")
            
            # Rb vertical resistor in left branch (y=80 to y=150)
            self.draw_res_v(self.bias_cvs, 160, 80, 160, 150, label="Rb")
            
            # Wire from Rb to Base pin (252, 150)
            self.bias_cvs.create_line(160, 150, 252, 150, width=2.5, fill="#000000")
            
            # Emitter to ground
            self.bias_cvs.create_line(292, 178, 292, 255, width=2.5, fill="#000000")
            self.draw_gnd(self.bias_cvs, 292, 255)
            
            inputs = [("Vcc (V):", "10"), ("Rb (kΩ):", "250"), ("Rc (kΩ):", "4.7"), ("Beta:", "90")]

        for i, (lbl, default) in enumerate(inputs):
            ctk.CTkLabel(self.bias_form, text=lbl, font=RETRO_FONT, text_color="#000000").grid(row=i//3, column=(i%3)*2, padx=5, pady=5, sticky="e")
            e = ctk.CTkEntry(self.bias_form, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0, width=80)
            e.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5, sticky="w")
            e.insert(0, default)
            self.bjt_bias_entries[lbl] = e
            
        btn = ctk.CTkButton(self.bias_form, text="Calculate Q-Point & Render DC Load Line", font=RETRO_FONT, fg_color="#27C93F", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_bias(choice))
        btn.grid(row=3, column=0, columnspan=6, pady=10)
        self.calc_bias(choice)

    def calc_bias(self, choice):
        """
        =============================================================================
        BJT DC BIASING TOPOLOGIES & LOAD LINE Q-POINT SOLVER
        =============================================================================
        Calculates quiescent operating point Q(Vce, Ic) across 4 major bias topologies:
        
        1. Fixed Bias:
           - Ib = (Vcc - Vbe) / Rb
           - Ic = β * Ib
           - Vce = Vcc - Ic * Rc
           - Simplest configuration, but highly β-dependent and thermally unstable.
           
        2. Voltage Divider Bias (Thevenin Equivalent):
           - Vth = Vcc * [R2 / (R1 + R2)]
           - Rth = R1 || R2 = (R1 * R2) / (R1 + R2)
           - Ib = (Vth - Vbe) / [Rth + (β + 1) * Re]
           - Ic = β * Ib; Vce = Vcc - Ic * (Rc + Re)
           - Most thermally stable configuration; virtually immune to β variations.
           
        3. Emitter Bias:
           - Ib = (Vcc - Vbe) / [Rb + (β + 1) * Re]
           - Emitter degeneration provides negative feedback stabilizing Ic against temperature.
           
        4. Collector Feedback Bias:
           - Base resistor returned to collector instead of Vcc rail.
           - Ib = (Vcc - Vbe) / [Rb + β * Rc]
           - Negative feedback loop stabilizes Q-point against β drift.
           
        Load Line Analysis:
           - Cutoff Voltage: Vce_cutoff = Vcc (Ic = 0)
           - Saturation Current: Ic_sat = Vcc / (Rc + Re) (Vce = 0)
        =============================================================================
        """
        try:
            Vbe = 0.7
            if choice == "Fixed Bias":
                Vcc = float(self.bjt_bias_entries["Vcc (V):"].get())
                Rb = float(self.bjt_bias_entries["Rb (kΩ):"].get()) * 1000
                Rc = float(self.bjt_bias_entries["Rc (kΩ):"].get()) * 1000
                beta = float(self.bjt_bias_entries["Beta:"].get())
                Re = 0
                Ib = (Vcc - Vbe) / Rb
                Ic = beta * Ib
                Vce = Vcc - Ic * Rc
            elif choice == "Voltage Divider":
                Vcc = float(self.bjt_bias_entries["Vcc (V):"].get())
                R1 = float(self.bjt_bias_entries["R1 (kΩ):"].get()) * 1000
                R2 = float(self.bjt_bias_entries["R2 (kΩ):"].get()) * 1000
                Rc = float(self.bjt_bias_entries["Rc (kΩ):"].get()) * 1000
                Re = float(self.bjt_bias_entries["Re (kΩ):"].get()) * 1000
                beta = float(self.bjt_bias_entries["Beta:"].get())
                Vth = Vcc * R2 / (R1 + R2)
                Rth = (R1 * R2) / (R1 + R2)
                Ib = (Vth - Vbe) / (Rth + (beta + 1) * Re)
                Ic = beta * Ib
                Vce = Vcc - Ic * (Rc + Re)
            elif choice == "Emitter Bias":
                Vcc = float(self.bjt_bias_entries["Vcc (V):"].get())
                Rb = float(self.bjt_bias_entries["Rb (kΩ):"].get()) * 1000
                Rc = float(self.bjt_bias_entries["Rc (kΩ):"].get()) * 1000
                Re = float(self.bjt_bias_entries["Re (kΩ):"].get()) * 1000
                beta = float(self.bjt_bias_entries["Beta:"].get())
                Ib = (Vcc - Vbe) / (Rb + (beta + 1) * Re)
                Ic = beta * Ib
                Vce = Vcc - Ic * (Rc + Re)
            elif choice == "Collector Feedback":
                Vcc = float(self.bjt_bias_entries["Vcc (V):"].get())
                Rb = float(self.bjt_bias_entries["Rb (kΩ):"].get()) * 1000
                Rc = float(self.bjt_bias_entries["Rc (kΩ):"].get()) * 1000
                Re = 0
                beta = float(self.bjt_bias_entries["Beta:"].get())
                Ib = (Vcc - Vbe) / (Rb + beta * Rc)
                Ic = beta * Ib
                Vce = Vcc - Ic * Rc
                
            Icsat = Vcc / (Rc + Re) * 1000 # in mA
            res_txt = (
                f"> Base Current (Ib) = {Ib*1e6:.2f} µA\n"
                f"> Collector Current (Ic) = {Ic*1000:.2f} mA | Ie = {(Ic+Ib)*1000:.2f} mA\n"
                f"> Collector-Emitter Voltage (Vce) = {Vce:.2f} V\n"
                f"> Operating Point Q = ({Vce:.2f} V, {Ic*1000:.2f} mA) | Saturation Limit Icsat = {Icsat:.2f} mA"
            )
            self.lbl_bias_out.configure(text=res_txt, text_color="#27C93F")
            self.calc_history_log += f"\n[BJT DC BIASING - {choice}]\n{res_txt}\nTimestamp: {datetime.datetime.now()}\n"
            
            # Dynamic 2D Matplotlib DC Load Line & Collector Family of Curves
            for w in self.bias_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.2, 2.8), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#FFFFFF")
            
            vce_vals = np.linspace(0, Vcc*1.15, 200)
            # Plot DC Load Line
            ic_loadline = np.maximum(0, (Vcc - vce_vals) / ((Rc + Re) / 1000.0))
            ax.plot(vce_vals, ic_loadline, color="#FF3333", lw=3, label=f"DC Load Line (Icsat={Icsat:.1f}mA)")
            
            # Plot family of collector curves
            ib_multipliers = [0.5, 1.0, 1.5, 2.0]
            for mult in ib_multipliers:
                ib_curr = Ib * mult
                ic_sat_level = beta * ib_curr * 1000
                # Knee shape using tanh
                curve = ic_sat_level * np.tanh(vce_vals / 0.5) * (1 + 0.02 * vce_vals)
                lbl = f"Ib={ib_curr*1e6:.0f}µA" if mult == 1.0 else None
                ax.plot(vce_vals, curve, color="#0055FF", lw=1.8, alpha=0.85 if mult==1.0 else 0.45, label=lbl)
                
            ax.plot(Vce, Ic*1000, marker='o', markersize=10, color="#FFDC00", markeredgecolor="#000000", markeredgewidth=2, label=f"Q-Point ({Vce:.1f}V, {Ic*1000:.1f}mA)")
            ax.axvline(Vce, color="#FFDC00", linestyle="--", alpha=0.6)
            ax.axhline(Ic*1000, color="#FFDC00", linestyle="--", alpha=0.6)
            
            ax.set_title(f"BJT Output Characteristics & DC Load Line ({choice})", fontsize=11, fontweight="bold")
            ax.set_xlabel("Collector-Emitter Voltage Vce (V)", fontsize=9, fontweight="bold")
            ax.set_ylabel("Collector Current Ic (mA)", fontsize=9, fontweight="bold")
            ax.set_xlim(0, Vcc*1.15)
            ax.set_ylim(0, Icsat*1.2)
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(fontsize=8, loc="upper right")
            
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.bias_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_bias_out.configure(text=f"> ERR: {e}", text_color="#FF5F56")

    # ==================== V. BJT AC SMALL-SIGNAL ====================
    def show_bjt_ac(self):
        self.clear_content()
        self.create_retro_title("V. BJT AC SMALL-SIGNAL AMPLIFIER")
        self.create_toolbar(reset_cmd=self.reset_ac)
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(box, text="Configuration:", font=RETRO_FONT, text_color="#000000").pack(pady=5)
        self.ac_combo = ctk.CTkComboBox(
            box, 
            values=["Common Emitter", "Common Emitter (Unbypassed)", "Emitter Follower"], 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_ac
        )
        self.ac_combo.pack(pady=5)
        
        self.ac_form = ctk.CTkFrame(box, fg_color="transparent")
        self.ac_form.pack(pady=5)
        
        res_frame = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res_frame.pack(fill="x", padx=20, pady=5)
        self.lbl_ac_out = ctk.CTkLabel(res_frame, text="> Av = ?", font=RETRO_FONT, text_color="#27C93F", justify="left")
        self.lbl_ac_out.pack(padx=10, pady=10, anchor="w")

        self.ac_plot_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.ac_plot_frame.pack(fill="x", padx=20, pady=10)
        
        self.update_ac("Common Emitter")

    def reset_ac(self):
        choice = self.ac_combo.get()
        self.update_ac(choice)

    def update_ac(self, choice):
        for w in self.ac_form.winfo_children(): w.destroy()
        self.ac_entries = {}
        
        if choice == "Common Emitter":
            inputs = [("Rc (kΩ):", "2.2"), ("r_e (Ω):", "10"), ("Vin_peak (mV):", "10")]
        elif choice == "Common Emitter (Unbypassed)":
            inputs = [("Rc (kΩ):", "2.2"), ("Re (kΩ):", "1.0"), ("r_e (Ω):", "10"), ("Vin_peak (mV):", "10")]
        elif choice == "Emitter Follower":
            inputs = [("Re (kΩ):", "2.2"), ("r_e (Ω):", "10"), ("Vin_peak (mV):", "10")]
            
        for i, (lbl, default) in enumerate(inputs):
            ctk.CTkLabel(self.ac_form, text=lbl, font=RETRO_FONT, text_color="#000000").grid(row=i, column=0, padx=5, pady=4, sticky="e")
            e = ctk.CTkEntry(self.ac_form, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0)
            e.grid(row=i, column=1, padx=5, pady=4)
            e.insert(0, default)
            self.ac_entries[lbl] = e
            
        btn = ctk.CTkButton(self.ac_form, text="Calculate Small-Signal Gain & Render Scope", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_ac(choice))
        btn.grid(row=len(inputs), column=0, columnspan=2, pady=10)
        self.calc_ac(choice)

    def calc_ac(self, choice):
        """
        =============================================================================
        BJT SMALL-SIGNAL AC ANALYSIS & TIME-DOMAIN OSCILLOSCOPE TRACE
        =============================================================================
        Evaluates BJT linear small-signal models (re parameter equivalent circuit):
        
        Dynamic Emitter Resistance:
           re = 26 mV / Ie_DC (at room temperature T = 300 K)
           
        1. Common Emitter (Bypassed Emitter Capacitor Ce):
           - AC voltage gain: Av = -Rc / re
           - 180° phase inversion between base input and collector output.
           - High voltage amplification.
           
        2. Common Emitter (Unbypassed Emitter Resistor Re):
           - Negative feedback degeneration lowers gain but raises input impedance.
           - AC voltage gain: Av = -Rc / (re + Re)
           - 180° phase inversion preserved.
           
        3. Common Collector / Emitter Follower:
           - Output taken across emitter resistor: Av = Re / (re + Re) ≈ 1
           - Phase shift: 0° (in-phase output).
           - High input impedance, low output impedance (ideal unity buffer).
        =============================================================================
        """
        try:
            Vin_peak = float(self.ac_entries["Vin_peak (mV):"].get())
            if choice == "Common Emitter":
                Rc = float(self.ac_entries["Rc (kΩ):"].get()) * 1000
                re = float(self.ac_entries["r_e (Ω):"].get())
                Av = -Rc / re
                phase_shift = 180
            elif choice == "Common Emitter (Unbypassed)":
                Rc = float(self.ac_entries["Rc (kΩ):"].get()) * 1000
                Re = float(self.ac_entries["Re (kΩ):"].get()) * 1000
                re = float(self.ac_entries["r_e (Ω):"].get())
                Av = -Rc / (re + Re)
                phase_shift = 180
            elif choice == "Emitter Follower":
                Re = float(self.ac_entries["Re (kΩ):"].get()) * 1000
                re = float(self.ac_entries["r_e (Ω):"].get())
                Av = Re / (Re + re)
                phase_shift = 0
                
            Vout_peak = abs(Av) * Vin_peak
            res_txt = (
                f"> Voltage Gain (Av) = {Av:.2f} ({20*np.log10(abs(Av)):.1f} dB)\n"
                f"> Phase Inversion = {phase_shift}°\n"
                f"> Output Peak Voltage (Vout) = {Vout_peak:.1f} mV ({Vout_peak/1000:.3f} V)"
            )
            self.lbl_ac_out.configure(text=res_txt, text_color="#27C93F")
            self.calc_history_log += f"\n[BJT AC SMALL-SIGNAL - {choice}]\n{res_txt}\nTimestamp: {datetime.datetime.now()}\n"
            
            # Dynamic Oscilloscope View
            for w in self.ac_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.2, 2.7), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#FFFFFF")
            
            t = np.linspace(0, 0.002, 500) # 1 kHz
            f_sig = 1000
            omega = 2 * np.pi * f_sig
            v_in_t = Vin_peak * np.sin(omega * t)
            v_out_t = Av * Vin_peak * np.sin(omega * t)
            
            ax.plot(t*1000, v_in_t, color="#0055FF", lw=2, linestyle="--", label=f"Input vin(t) [{Vin_peak}mV]")
            ax.plot(t*1000, v_out_t, color="#FF3333", lw=2.5, label=f"Amplified vout(t) [{abs(Vout_peak):.1f}mV, {phase_shift}°]")
            ax.axhline(0, color="#000000", lw=1)
            ax.set_title(f"AC Amplifier Scope Trace - {choice} (Gain = {Av:.1f})", fontsize=11, fontweight="bold")
            ax.set_xlabel("Time (milliseconds)", fontsize=9, fontweight="bold")
            ax.set_ylabel("Signal Voltage (mV)", fontsize=9, fontweight="bold")
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(fontsize=8, loc="upper right")
            
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.ac_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_ac_out.configure(text=f"> ERR: {e}", text_color="#FF5F56")

    # ==================== VI. FET FUNDAMENTALS & AMPS ====================
    def show_fet(self):
        self.clear_content()
        self.create_retro_title("VI. FET FUNDAMENTALS, MOSFETS & CMOS")
        from practical_applications import get_practical_example
        ctk.CTkLabel(self.content_frame, text=get_practical_example('fet'), font=('Helvetica', 11, 'italic'), text_color='#333333', wraplength=500, justify='left').pack(pady=(0, 10), padx=20)
        self.create_toolbar(reset_cmd=self.reset_fet)
        
        top = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top.pack(pady=5)
        
        ctk.CTkLabel(top, text="FET Category:", font=RETRO_FONT, text_color="#000000").pack(side="left", padx=5)
        self.fet_combo = ctk.CTkComboBox(
            top, 
            values=["JFET", "D-MOSFET", "E-MOSFET", "CMOS Inverter"], 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_fet
        )
        self.fet_combo.pack(side="left", padx=5)
        
        self.fet_cvs = ctk.CTkCanvas(self.content_frame, width=560, height=260, bg="#FFF5EE", highlightthickness=4, highlightbackground="#000000")
        self.fet_cvs.pack(pady=10)
        
        self.fet_form = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        self.fet_form.pack(pady=5, fill="x", padx=20)
        
        res_frame = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res_frame.pack(fill="x", padx=20, pady=5)
        self.lbl_fet_out = ctk.CTkLabel(res_frame, text="> ...", font=RETRO_FONT, text_color="#27C93F", justify="left")
        self.lbl_fet_out.pack(padx=10, pady=10, anchor="w")

        self.fet_plot_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.fet_plot_frame.pack(fill="x", padx=20, pady=10)
        
        self.update_fet("JFET")

    def reset_fet(self):
        choice = self.fet_combo.get()
        self.update_fet(choice)

    def update_fet(self, choice):
        self.fet_cvs.delete("all")
        for w in self.fet_form.winfo_children(): w.destroy()
        self.fet_entries = {}

        if choice == "JFET":
            self.draw_jfet_n(self.fet_cvs, 280, 130, label="2N5458")
            self.fet_cvs.create_text(292, 18, text="+ VDD", font=("Helvetica", 12, "bold"), fill="#FF3333")
            self.draw_res_v(self.fet_cvs, 292, 30, 292, 102, label="RD")
            
            self.fet_cvs.create_line(252, 130, 160, 130, width=2.5, fill="#000000")
            self.draw_res_v(self.fet_cvs, 160, 130, 160, 210, label="RG")
            self.draw_gnd(self.fet_cvs, 160, 210)
            
            self.fet_cvs.create_line(292, 158, 292, 210, width=2.5, fill="#000000")
            self.draw_gnd(self.fet_cvs, 292, 210)
            
            inputs = [("Idss (mA):", "10"), ("Vp (V):", "-4"), ("Vgs (V):", "-2")]
            btn_txt = "Calculate & Plot Shockley Transfer Curve"

        elif choice == "D-MOSFET":
            self.draw_dmos_n(self.fet_cvs, 280, 130, label="Depletion")
            self.fet_cvs.create_text(292, 18, text="+ VDD", font=("Helvetica", 12, "bold"), fill="#FF3333")
            self.draw_res_v(self.fet_cvs, 292, 30, 292, 102, label="RD")
            
            self.fet_cvs.create_line(252, 130, 170, 130, width=2.5, fill="#000000")
            self.fet_cvs.create_text(145, 130, text="VGS", font=("Helvetica", 11, "bold"), fill="#0055FF")
            
            self.fet_cvs.create_line(292, 158, 292, 210, width=2.5, fill="#000000")
            self.draw_gnd(self.fet_cvs, 292, 210)
            
            inputs = [("Idss (mA):", "10"), ("Vp (V):", "-4"), ("Vgs (V):", "-2")]
            btn_txt = "Calculate & Plot Transfer Curve"

        elif choice == "E-MOSFET":
            self.draw_emos_n(self.fet_cvs, 280, 130, label="Enhance")
            self.fet_cvs.create_text(292, 18, text="+ VDD", font=("Helvetica", 12, "bold"), fill="#FF3333")
            self.draw_res_v(self.fet_cvs, 292, 30, 292, 102, label="RD")
            
            self.fet_cvs.create_line(252, 130, 170, 130, width=2.5, fill="#000000")
            self.fet_cvs.create_text(145, 130, text="VGS", font=("Helvetica", 11, "bold"), fill="#0055FF")
            
            self.fet_cvs.create_line(292, 158, 292, 210, width=2.5, fill="#000000")
            self.draw_gnd(self.fet_cvs, 292, 210)
            
            inputs = [("k (mA/V^2):", "0.3"), ("Vth (V):", "2.0"), ("Vgs (V):", "5")]
            btn_txt = "Calculate & Plot E-MOSFET Curve"

        elif choice == "CMOS Inverter":
            self.fet_cvs.create_text(280, 18, text="+ VDD", font=("Helvetica", 12, "bold"), fill="#FF3333")
            self.fet_cvs.create_line(280, 28, 280, 50, width=2.5, fill="#000000")
            
            # PMOS
            self.fet_cvs.create_line(260, 50, 280, 50, width=2.5, fill="#000000")
            self.fet_cvs.create_line(260, 45, 260, 85, width=3.5, fill="#000000")
            self.fet_cvs.create_line(252, 45, 252, 85, width=2.5, fill="#000000")
            self.fet_cvs.create_oval(242, 60, 252, 70, width=2, outline="#000000", fill="#FFFFFF")
            self.fet_cvs.create_line(210, 65, 242, 65, width=2.5, fill="#000000")
            self.fet_cvs.create_line(260, 80, 280, 80, width=2.5, fill="#000000")
            self.fet_cvs.create_text(310, 65, text="PMOS", font=("Helvetica", 10, "bold"), fill="#FF3333")
            
            # Connection Node
            self.fet_cvs.create_line(280, 80, 280, 140, width=2.5, fill="#000000")
            self.fet_cvs.create_line(280, 110, 380, 110, width=2.5, fill="#000000")
            self.fet_cvs.create_oval(375, 105, 385, 115, fill="#0055FF")
            self.fet_cvs.create_text(415, 110, text="Vout", font=("Helvetica", 11, "bold"), fill="#0055FF")
            
            # NMOS
            self.fet_cvs.create_line(260, 140, 280, 140, width=2.5, fill="#000000")
            self.fet_cvs.create_line(260, 135, 260, 175, width=3.5, fill="#000000")
            self.fet_cvs.create_line(252, 135, 252, 175, width=2.5, fill="#000000")
            self.fet_cvs.create_line(210, 155, 252, 155, width=2.5, fill="#000000")
            self.fet_cvs.create_line(260, 170, 280, 170, width=2.5, fill="#000000")
            self.fet_cvs.create_text(310, 155, text="NMOS", font=("Helvetica", 10, "bold"), fill="#0055FF")
            
            # Common Gate
            self.fet_cvs.create_line(210, 65, 210, 155, width=2.5, fill="#000000")
            self.fet_cvs.create_line(210, 110, 150, 110, width=2.5, fill="#000000")
            self.fet_cvs.create_text(125, 110, text="Vin", font=("Helvetica", 11, "bold"), fill="#000000")
            
            # Ground
            self.fet_cvs.create_line(280, 170, 280, 210, width=2.5, fill="#000000")
            self.draw_gnd(self.fet_cvs, 280, 210)
            
            inputs = [("VDD (V):", "5"), ("Vin (V):", "0")]
            btn_txt = "Evaluate Output & Plot VTC"

        for i, (lbl, default) in enumerate(inputs):
            ctk.CTkLabel(self.fet_form, text=lbl, font=RETRO_FONT, text_color="#000000").grid(row=i//3, column=(i%3)*2, padx=5, pady=5, sticky="e")
            e = ctk.CTkEntry(self.fet_form, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0, width=80)
            e.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5, sticky="w")
            e.insert(0, default)
            self.fet_entries[lbl] = e
            
        btn = ctk.CTkButton(self.fet_form, text=btn_txt, font=RETRO_FONT, fg_color="#FFBD2E", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_fet(choice))
        btn.grid(row=3, column=0, columnspan=6, pady=10)
        self.calc_fet(choice)

    def calc_fet(self, choice):
        """
        =============================================================================
        FIELD-EFFECT TRANSISTOR (FET) TRANSFER CHARACTERS & CMOS DYNAMICS
        =============================================================================
        1. JFET and Depletion-MOSFET (D-MOSFET) Shockley Equation:
           - Conduction via majority carriers controlled by gate reverse bias.
           - Id = Idss * [1 - (Vgs / Vp)]^2
           - Transconductance:
             gm0 = 2 * Idss / |Vp|
             gm = gm0 * [1 - (Vgs / Vp)]
             
        2. Enhancement-MOSFET (E-MOSFET) Square-Law Model:
           - Requires threshold voltage Vth to invert the channel.
           - For Vgs > Vth (Saturation Region):
             Id = k * (Vgs - Vth)^2
             gm = 2 * k * (Vgs - Vth)
           - For Vgs <= Vth: Id = 0 (Cutoff)
           
        3. CMOS Inverter (Complementary MOS: PMOS Pull-Up + NMOS Pull-Down):
           - Rail-to-rail voltage transfer curve (VTC).
           - Low static dissipation: P_static = 0 because only one transistor is ON at steady state.
           - Switching threshold: Vth_inv ≈ VDD / 2
        =============================================================================
        """
        try:
            if choice in ["JFET", "D-MOSFET"]:
                Idss = float(self.fet_entries["Idss (mA):"].get())
                Vp = float(self.fet_entries["Vp (V):"].get())
                Vgs = float(self.fet_entries["Vgs (V):"].get())
                Id = Idss * ((1 - Vgs/Vp)**2)
                gmo = 2 * Idss / abs(Vp)
                gm = gmo * (1 - Vgs/Vp)
                res_txt = (
                    f"> Drain Current (Id) = {Id:.2f} mA\n"
                    f"> Transconductance (gm) = {gm:.2f} mS (gm0 = {gmo:.2f} mS)\n"
                    f"> Shockley Transfer Equation: Id = Idss * [1 - Vgs/Vp]^2"
                )
            elif choice == "E-MOSFET":
                k = float(self.fet_entries["k (mA/V^2):"].get())
                Vth = float(self.fet_entries["Vth (V):"].get())
                Vgs = float(self.fet_entries["Vgs (V):"].get())
                Id = k * ((Vgs - Vth)**2) if Vgs > Vth else 0
                gm = 2 * k * (Vgs - Vth) if Vgs > Vth else 0
                res_txt = (
                    f"> Drain Current (Id) = {Id:.2f} mA\n"
                    f"> Transconductance (gm) = {gm:.2f} mS\n"
                    f"> Square-Law Model: Id = k * (Vgs - Vth)^2"
                )
            elif choice == "CMOS Inverter":
                VDD = float(self.fet_entries["VDD (V):"].get())
                Vin = float(self.fet_entries["Vin (V):"].get())
                Vout = VDD if Vin < VDD/2 else 0
                state = "LOGIC HIGH (1)" if Vout > VDD/2 else "LOGIC LOW (0)"
                res_txt = (
                    f"> CMOS Inverter Output (Vout) = {Vout:.2f} V [{state}]\n"
                    f"> Switching Threshold Vth = {VDD/2:.2f} V\n"
                    f"> Zero Static Power Dissipation: Pstatic ≈ 0 W"
                )

            self.lbl_fet_out.configure(text=res_txt, text_color="#27C93F")
            self.calc_history_log += f"\n[FET CHARACTERISTICS - {choice}]\n{res_txt}\nTimestamp: {datetime.datetime.now()}\n"
            
            # Dynamic 2D Curves Plot
            for w in self.fet_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.2, 2.7), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#FFFFFF")
            
            if choice in ["JFET", "D-MOSFET"]:
                vgs_axis = np.linspace(Vp, 0, 200)
                id_axis = Idss * ((1 - vgs_axis/Vp)**2)
                ax.plot(vgs_axis, id_axis, color="#0055FF", lw=3, label="Transfer Curve Id(Vgs)")
                ax.plot(Vgs, Id, marker='o', markersize=9, color="#FF3333", label=f"Q-Point ({Vgs}V, {Id:.2f}mA)")
                ax.set_title(f"{choice} Parabolic Shockley Transfer Characteristic", fontsize=11, fontweight="bold")
                ax.set_xlabel("Gate-Source Voltage Vgs (V)", fontsize=9, fontweight="bold")
                ax.set_ylabel("Drain Current Id (mA)", fontsize=9, fontweight="bold")
            elif choice == "E-MOSFET":
                vgs_axis = np.linspace(0, Vth*2.5, 200)
                id_axis = np.where(vgs_axis > Vth, k * ((vgs_axis - Vth)**2), 0)
                ax.plot(vgs_axis, id_axis, color="#0055FF", lw=3, label="E-MOSFET Id(Vgs)")
                ax.axvline(Vth, color="#FFBD2E", linestyle="--", label=f"Vth ({Vth}V)")
                ax.plot(Vgs, Id, marker='o', markersize=9, color="#FF3333", label=f"Q-Point ({Vgs}V, {Id:.2f}mA)")
                ax.set_title("E-MOSFET Square-Law Transfer Curve", fontsize=11, fontweight="bold")
                ax.set_xlabel("Gate-Source Voltage Vgs (V)", fontsize=9, fontweight="bold")
                ax.set_ylabel("Drain Current Id (mA)", fontsize=9, fontweight="bold")
            elif choice == "CMOS Inverter":
                vin_axis = np.linspace(0, VDD, 300)
                # Sigmoid-like voltage transfer characteristic
                vout_axis = VDD / (1 + np.exp(15 * (vin_axis/VDD - 0.5)))
                ax.plot(vin_axis, vout_axis, color="#27C93F", lw=3, label="VTC Curve")
                ax.plot(Vin, Vout, marker='s', markersize=9, color="#FF3333", label=f"State ({Vin}V in, {Vout}V out)")
                ax.set_title("CMOS Inverter Voltage Transfer Characteristic (VTC)", fontsize=11, fontweight="bold")
                ax.set_xlabel("Input Voltage Vin (V)", fontsize=9, fontweight="bold")
                ax.set_ylabel("Output Voltage Vout (V)", fontsize=9, fontweight="bold")
                
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(fontsize=8, loc="upper right")
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.fet_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_fet_out.configure(text=f"> ERR: {e}", text_color="#FF5F56")

    # ==================== VII. 3D TRANSISTOR SURFACE VISUALIZER ====================
    def show_3d_surface(self):
        self.clear_content()
        self.create_retro_title("VII. 3D TRANSISTOR CHARACTERISTICS SURFACE")
        self.create_toolbar(reset_cmd=self.reset_3d_surface)
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(box, text="3D Electronic Manifold Visualizer:", font=RETRO_FONT, text_color="#000000").pack(pady=5)
        
        f = ctk.CTkFrame(box, fg_color="transparent")
        f.pack(pady=5)
        
        ctk.CTkLabel(f, text="Device:", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=5, pady=5)
        self.combo_3d_device = ctk.CTkComboBox(
            f, 
            values=["BJT Collector Surface Ic(Vce, Ib)", "JFET Drain Surface Id(Vds, Vgs)"], 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=3, 
            corner_radius=0
        )
        self.combo_3d_device.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(f, text="Beta (β) / Idss (mA):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=2, padx=5, pady=5)
        self.entry_3d_param = ctk.CTkEntry(f, width=70, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0)
        self.entry_3d_param.grid(row=0, column=3, padx=5, pady=5)
        self.entry_3d_param.insert(0, "100")
        
        btn = ctk.CTkButton(box, text="Render 3D Transistor Surface", font=RETRO_FONT, fg_color="#0055FF", text_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0, command=self.render_3d_surface)
        btn.pack(pady=10)

        self.plot_3d_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.plot_3d_frame.pack(fill="x", padx=20, pady=10)
        
        self.render_3d_surface()

    def reset_3d_surface(self):
        self.entry_3d_param.delete(0, "end")
        self.entry_3d_param.insert(0, "100")
        self.render_3d_surface()

    def render_3d_surface(self):
        """
        =============================================================================
        3D SOLID-STATE TRANSISTOR MANIFOLD VISUALIZATION ENGINE
        =============================================================================
        Computes continuous non-linear parametric bivariate surfaces:
        
        1. BJT Output Surface: Ic = f(Vce, Ib)
           - Active mode amplification: Ic ≈ β * Ib
           - Triode/Saturation Knee transition modeled via hyperbolic tangent tanh(Vce / 0.7)
           - Early effect (base-width modulation) modeled via factor (1 + Vce / 100.0)
           
        2. JFET Drain Surface: Id = f(Vds, Vgs)
           - Ohmic/Triode region: Id = Idss * [2(1 - Vgs/Vp)(Vds/|Vp|) - (Vds/|Vp|)^2]
           - Pinch-off / Saturation region: Id = Idss * [1 - Vgs/Vp]^2
        =============================================================================
        """
        try:
            dev = self.combo_3d_device.get()
            param = float(self.entry_3d_param.get())
            
            for w in self.plot_3d_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.4, 3.4), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            ax = fig.add_subplot(111, projection='3d')
            ax.set_facecolor("#FFFFFF")
            
            if "BJT" in dev:
                beta = param
                vce = np.linspace(0.1, 20, 40)
                ib_ua = np.linspace(5, 100, 40)
                VCE, IB = np.meshgrid(vce, ib_ua)
                # Realistic saturation knee + Early voltage effect
                IC = beta * (IB * 1e-3) * np.tanh(VCE / 0.7) * (1 + VCE / 100.0)
                surf = ax.plot_surface(VCE, IB, IC, cmap='coolwarm', edgecolor='k', lw=0.3, alpha=0.9)
                ax.set_title(f"3D Surface: BJT Collector Current Ic(Vce, Ib) [β={beta:.0f}]", fontsize=10, fontweight="bold")
                ax.set_xlabel("Vce (V)", fontsize=8, fontweight="bold")
                ax.set_ylabel("Ib (µA)", fontsize=8, fontweight="bold")
                ax.set_zlabel("Ic (mA)", fontsize=8, fontweight="bold")
            else:
                idss = param
                Vp = -4.0
                vds = np.linspace(0.1, 15, 40)
                vgs = np.linspace(Vp, 0, 40)
                VDS, VGS = np.meshgrid(vds, vgs)
                # JFET pinch-off & ohmic region
                v_pinch = VGS - Vp
                ID = np.where(VDS < v_pinch, 
                              idss * (2 * (1 - VGS/Vp) * (VDS/abs(Vp)) - (VDS/abs(Vp))**2),
                              idss * ((1 - VGS/Vp)**2))
                ID = np.maximum(0, ID)
                surf = ax.plot_surface(VDS, VGS, ID, cmap='viridis', edgecolor='k', lw=0.3, alpha=0.9)
                ax.set_title(f"3D Surface: JFET Drain Current Id(Vds, Vgs) [Idss={idss}mA]", fontsize=10, fontweight="bold")
                ax.set_xlabel("Vds (V)", fontsize=8, fontweight="bold")
                ax.set_ylabel("Vgs (V)", fontsize=8, fontweight="bold")
                ax.set_zlabel("Id (mA)", fontsize=8, fontweight="bold")
                
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.plot_3d_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
            self.calc_history_log += f"\n[3D TRANSISTOR SURFACE VISUALIZATION - {dev}]\nRendered successfully with param={param}\nTimestamp: {datetime.datetime.now()}\n"
            
        except Exception as e:
            if hasattr(self, 'lbl_tb_status'):
                self.lbl_tb_status.configure(text=f"3D Error: {e}", text_color="#FF3333")
