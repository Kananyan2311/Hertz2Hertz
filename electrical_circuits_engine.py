# =============================================================================
# ELECTRICAL_CIRCUITS_ENGINE.PY - EE FUNDAMENTALS & CIRCUIT SOLVER
# =============================================================================
# Architecture Overview:
#   This module implements the user interface and computation pipeline for
#   Electrical Engineering (EE) fundamentals:
#     1. Ohm's Law & DC Power Solver (V = I*R, P = V*I = I^2*R = V^2/R)
#     2. Series & Parallel Resistor Networks (Equivalent resistance, current distribution)
#     3. Multi-Loop Kirchhoff's Voltage Law (KVL) Mesh Matrix Solver ([R][I] = [V])
#     4. AC Steady-State Series R-L-C Circuit & Dual-Axis Waveform Generator
#
# Integration with MATLAB Engine:
#   Mathematical operations are dispatched to `matlab_manager` in `matlab_utils.py`,
#   which calls native `.m` functions in `matlab_code/ee_calc.m` on the official
#   MATLAB Engine (R2026b). If the engine is busy or booting, transparent pure-Python
#   fallbacks guarantee uninterrupted UI performance.
# =============================================================================

import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import os
from retro_ui import RETRO_FONT
from matlab_utils import matlab_manager

class ElectricalCircuitsEngine(ctk.CTkFrame):
    """
    CustomTkinter Frame hosting the Electrical Circuits engine.
    Controls the left navigation sidebar, canvas circuit drawings,
    dynamic entry forms, and matplotlib plot embeds.
    """
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Navigation
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#FFF5EE", border_width=4, border_color="#000000")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="💡 EE FUNDAMENTALS", font=RETRO_FONT, text_color="#000000")
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=20)

        self.nav_btns = {}
        self.btn_ohms = self.create_nav_btn("1. Ohm's Law & Power", self.show_ohms, 1, "ohms")
        self.btn_equiv = self.create_nav_btn("2. Series & Parallel", self.show_equiv, 2, "equiv")
        self.btn_kirchhoff = self.create_nav_btn("3. Kirchhoff (KVL/KCL)", self.show_kirchhoff, 3, "kirchhoff")
        self.btn_ac_rlc = self.create_nav_btn("4. AC RLC & Waveforms", self.show_ac_rlc, 4, "ac")

        # Main content area (Scrollable to prevent cramped UI)
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.calc_history_log = (
            "================================================================================\n"
            "FINAL PROJECT REPORT - ELECTRICAL CIRCUITS ENGINE\n"
            "STUDENTS: GONZALES, IVAN LAWRENCE F. & LO NIEVA, STEVEN\n"
            "SECTION: BSCPE241B | DATE: OCTOBER 5, 2026 | STATUS: VERIFIED [/]\n"
            "================================================================================\n"
        )
        
        self.show_ohms()

    def create_nav_btn(self, text, command, row, key):
        def wrapper():
            self.set_active_nav(key)
            command()

        btn = ctk.CTkButton(
            self.sidebar, 
            text=text, 
            font=("Helvetica", 12, "bold"), 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            hover_color="#BAE6FD", 
            command=wrapper
        )
        btn.grid(row=row, column=0, padx=10, pady=8, sticky="ew")
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
            filename = f"EE_Circuits_Report_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.calc_history_log)
                f.write(f"\nReport Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if hasattr(self, 'lbl_tb_status'):
                self.lbl_tb_status.configure(text=f"Saved: {filename}", text_color="#27C93F")
        except Exception as e:
            if hasattr(self, 'lbl_tb_status'):
                self.lbl_tb_status.configure(text=f"Export Error: {e}", text_color="#FF3333")

    def show_ohms(self):
        self.clear_content()
        self.create_retro_title("1. OHM'S LAW & POWER ⚡")
        from practical_applications import get_practical_example
        ctk.CTkLabel(self.content_frame, text=get_practical_example("ohms_law"), font=("Helvetica", 11, "italic"), text_color="#333333", wraplength=500, justify="left").pack(pady=(0, 10), padx=20)
        self.create_toolbar(reset_cmd=self.reset_ohms)
        
        cvs = ctk.CTkCanvas(self.content_frame, width=540, height=200, bg="#FFF5EE", highlightthickness=4, highlightbackground="#000000")
        cvs.pack(pady=10)
        
        # Battery on left
        cvs.create_line(80, 40, 80, 75, width=4, fill="#000000")
        cvs.create_line(50, 75, 110, 75, width=4, fill="#000000") # + plate
        cvs.create_line(65, 95, 95, 95, width=6, fill="#000000") # - plate
        cvs.create_line(80, 95, 80, 160, width=4, fill="#000000")
        cvs.create_text(35, 75, text="+", font=("Helvetica", 16, "bold"), fill="#FF3333")
        cvs.create_text(35, 95, text="-", font=("Helvetica", 16, "bold"), fill="#000000")
        cvs.create_text(35, 120, text="V (DC)", font=("Helvetica", 14, "bold"), fill="#FF3333")
        
        # Closed circuit loop
        cvs.create_line(80, 40, 460, 40, width=4, fill="#000000")
        cvs.create_line(460, 40, 460, 160, width=4, fill="#000000")
        cvs.create_line(80, 160, 200, 160, width=4, fill="#000000")
        cvs.create_line(340, 160, 460, 160, width=4, fill="#000000")
        
        # Resistor zigzag
        pts = [
            200, 160,
            215, 140,
            230, 180,
            245, 140,
            260, 180,
            275, 140,
            290, 180,
            305, 140,
            325, 180,
            340, 160
        ]
        cvs.create_line(*pts, width=4, fill="#0055FF")
        cvs.create_text(270, 115, text="Resistor (R)", font=("Helvetica", 14, "bold"), fill="#0055FF")
        
        # Current Arrow
        cvs.create_line(220, 25, 320, 25, arrow="last", arrowshape=(14, 18, 6), width=4, fill="#27C93F")
        cvs.create_text(270, 10, text="Current I  -->", font=("Helvetica", 13, "bold"), fill="#27C93F")
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(box, text="Enter ANY TWO values to solve for the rest:", font=RETRO_FONT, text_color="#000000").pack(pady=8)
        
        f = ctk.CTkFrame(box, fg_color="transparent")
        f.pack()
        
        self.ohm_entries = {}
        defaults = {"Voltage (V)": "12", "Resistance (R)": "4", "Current (I)": "", "Power (P)": ""}
        for i, lbl in enumerate(["Voltage (V)", "Current (I)", "Resistance (R)", "Power (P)"]):
            ctk.CTkLabel(f, text=f"{lbl}:", font=RETRO_FONT, text_color="#000000").grid(row=i//2, column=(i%2)*2, padx=10, pady=5)
            ent = ctk.CTkEntry(f, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=4, corner_radius=0)
            ent.grid(row=i//2, column=(i%2)*2+1, pady=5)
            if defaults[lbl]:
                ent.insert(0, defaults[lbl])
            self.ohm_entries[lbl] = ent
            
        btn = ctk.CTkButton(box, text="Calculate & Plot V-I & Power Curves", font=RETRO_FONT, fg_color="#27C93F", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=self.calc_ohms)
        btn.pack(pady=10)
        
        res = ctk.CTkFrame(box, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res.pack(fill="x", padx=20, pady=10)
        self.lbl_ohm_res = ctk.CTkLabel(res, text="> Results...", font=RETRO_FONT, text_color="#FFBD2E", justify="left")
        self.lbl_ohm_res.pack(padx=10, pady=10, anchor="w")

        # Container for Dynamic Plot
        self.ohm_plot_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.ohm_plot_frame.pack(fill="x", padx=20, pady=10)
        self.calc_ohms()

    def reset_ohms(self):
        for lbl, ent in self.ohm_entries.items():
            ent.delete(0, "end")
        self.ohm_entries["Voltage (V)"].insert(0, "12")
        self.ohm_entries["Resistance (R)"].insert(0, "4")
        self.calc_ohms()

    def calc_ohms(self):
        """
        Calculates unknown electrical parameters from Ohm's Law (V = I * R)
        and Joule's Law of Electric Power (P = V * I = I^2 * R = V^2 / R).
        
        Algorithm:
          1. Extracts the 4 input fields: Voltage (V), Current (I), Resistance (R), Power (P).
          2. Validates that exactly TWO non-empty values were provided.
          3. Passes values to the MATLAB Engine backend (`matlab_manager.ee_ohms_law`).
          4. Updates the terminal output display with solved engineering quantities.
          5. Generates two synchronized matplotlib graphs:
             - Subplot 1: Linear V-I characteristic line with operating Q-point.
             - Subplot 2: Parabolic power dissipation curve P(I) = I^2 * R.
        """
        try:
            # Step 1: Read raw strings and convert non-empty inputs to floating point values
            v_str = self.ohm_entries["Voltage (V)"].get().strip()
            i_str = self.ohm_entries["Current (I)"].get().strip()
            r_str = self.ohm_entries["Resistance (R)"].get().strip()
            p_str = self.ohm_entries["Power (P)"].get().strip()
            
            v = float(v_str) if v_str else None
            i = float(i_str) if i_str else None
            r = float(r_str) if r_str else None
            p = float(p_str) if p_str else None
            
            # Step 2: Ensure user entered exactly two values
            known_cnt = sum(1 for x in [v, i, r, p] if x is not None)
            if known_cnt != 2:
                self.lbl_ohm_res.configure(text="> ERR: Enter exactly TWO values to solve the remaining two.", text_color="#FF5F56")
                return
                
            # Step 3: Dispatch calculation to MATLAB Engine backend (ee_calc.m)
            v, i, r, p = matlab_manager.ee_ohms_law(v, i, r, p)
                
            # Step 4: Display formatted engineering results
            out_text = (
                f"> Voltage (V)    = {v:.3f} V\n"
                f"> Current (I)    = {i:.3f} A ({i*1000:.1f} mA)\n"
                f"> Resistance (R) = {r:.3f} Ω\n"
                f"> Power (P)      = {p:.3f} W\n"
                f"{matlab_manager.get_status_text()}"
            )


            
            self.lbl_ohm_res.configure(text=out_text, text_color="#27C93F")
            
            self.calc_history_log += f"\n[OHMS LAW CALCULATION]\n{out_text}\nTimestamp: {datetime.datetime.now()}\n"
            
            # Dynamic 2D Graph (V-I Line & Power Parabola)
            for w in self.ohm_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.2, 2.8), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            
            # Subplot 1: V-I Curve
            ax1 = fig.add_subplot(121)
            ax1.set_facecolor("#FFFFFF")
            i_max = max(i * 2, 2.0)
            i_arr = np.linspace(0, i_max, 100)
            v_arr = i_arr * r
            ax1.plot(i_arr, v_arr, color="#0055FF", lw=3, label=f"V=I·R (R={r:.1f}Ω)")
            ax1.plot(i, v, marker='o', markersize=8, color="#FF3333", label=f"Q ({i:.2f}A, {v:.2f}V)")
            ax1.axhline(v, color="#FF3333", linestyle="--", alpha=0.5)
            ax1.axvline(i, color="#FF3333", linestyle="--", alpha=0.5)
            ax1.set_title("V-I Characteristic", fontsize=11, fontweight="bold")
            ax1.set_xlabel("Current I (A)", fontsize=9, fontweight="bold")
            ax1.set_ylabel("Voltage V (V)", fontsize=9, fontweight="bold")
            ax1.grid(True, linestyle=":", alpha=0.6)
            ax1.legend(fontsize=8, loc="upper left")
            
            # Subplot 2: Power Curve
            ax2 = fig.add_subplot(122)
            ax2.set_facecolor("#FFFFFF")
            p_arr = (i_arr**2) * r
            ax2.plot(i_arr, p_arr, color="#27C93F", lw=3, label=f"P=I²·R")
            ax2.plot(i, p, marker='s', markersize=8, color="#FFBD2E", label=f"P ({p:.2f}W)")
            ax2.axhline(p, color="#FFBD2E", linestyle="--", alpha=0.5)
            ax2.axvline(i, color="#FFBD2E", linestyle="--", alpha=0.5)
            ax2.set_title("Power Dissipation", fontsize=11, fontweight="bold")
            ax2.set_xlabel("Current I (A)", fontsize=9, fontweight="bold")
            ax2.set_ylabel("Power P (W)", fontsize=9, fontweight="bold")
            ax2.grid(True, linestyle=":", alpha=0.6)
            ax2.legend(fontsize=8, loc="upper left")
            
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.ohm_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_ohm_res.configure(text=f"> ERR: {str(e)}", text_color="#FF5F56")

    def show_equiv(self):
        self.clear_content()
        self.create_retro_title("2. SERIES & PARALLEL RESISTORS 🔌")
        from practical_applications import get_practical_example
        ctk.CTkLabel(self.content_frame, text=get_practical_example('equiv_res'), font=('Helvetica', 11, 'italic'), text_color='#333333', wraplength=500, justify='left').pack(pady=(0, 10), padx=20)
        self.create_toolbar(reset_cmd=self.reset_equiv)
        
        self.equiv_mode = ctk.StringVar(value="Series")
        mode_combo = ctk.CTkComboBox(
            self.content_frame, 
            values=["Series", "Parallel"], 
            variable=self.equiv_mode, 
            font=RETRO_FONT, 
            fg_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_equiv_ui
        )
        mode_combo.pack(pady=5)

        self.equiv_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.equiv_container.pack(fill="both", expand=True)
        self.update_equiv_ui()

    def reset_equiv(self):
        self.ent_res.delete(0, "end")
        self.ent_res.insert(0, "100 220 330")
        self.ent_vin.delete(0, "end")
        self.ent_vin.insert(0, "12")
        self.calc_equiv()

    def update_equiv_ui(self, choice=None):
        for widget in self.equiv_container.winfo_children():
            widget.destroy()
            
        mode = self.equiv_mode.get()
        cvs = ctk.CTkCanvas(self.equiv_container, width=540, height=200, bg="#FFF5EE", highlightthickness=4, highlightbackground="#000000")
        cvs.pack(pady=10)
        
        if mode == "Series":
            cvs.create_text(270, 25, text="-- SERIES RESISTORS SCHEMATIC --", font=("Helvetica", 14, "bold"), fill="#000000")
            cvs.create_line(60, 100, 120, 100, width=4, fill="#000000")
            pts_r1 = [120, 100, 130, 80, 145, 120, 160, 80, 175, 120, 190, 80, 205, 120, 215, 100]
            cvs.create_line(*pts_r1, width=4, fill="#0055FF")
            cvs.create_text(168, 145, text="Resistor R1", font=("Helvetica", 13, "bold"), fill="#0055FF")
            
            cvs.create_line(215, 100, 290, 100, width=4, fill="#000000")
            
            pts_r2 = [290, 100, 300, 80, 315, 120, 330, 80, 345, 120, 360, 80, 375, 120, 385, 100]
            cvs.create_line(*pts_r2, width=4, fill="#FF3333")
            cvs.create_text(338, 145, text="Resistor R2", font=("Helvetica", 13, "bold"), fill="#FF3333")
            
            cvs.create_line(385, 100, 480, 100, width=4, fill="#000000")
            cvs.create_oval(54, 94, 66, 106, fill="#000000")
            cvs.create_oval(474, 94, 486, 106, fill="#000000")
            cvs.create_text(60, 75, text="IN (+)", font=("Helvetica", 11, "bold"), fill="#000000")
            cvs.create_text(480, 75, text="OUT (-)", font=("Helvetica", 11, "bold"), fill="#000000")
        else:
            cvs.create_text(270, 22, text="-- PARALLEL RESISTORS SCHEMATIC --", font=("Helvetica", 14, "bold"), fill="#000000")
            cvs.create_line(60, 105, 140, 105, width=4, fill="#000000")
            cvs.create_oval(134, 99, 146, 111, fill="#000000")
            cvs.create_line(140, 60, 140, 150, width=4, fill="#000000")
            
            cvs.create_line(140, 60, 190, 60, width=4, fill="#000000")
            pts_pr1 = [190, 60, 200, 45, 215, 75, 230, 45, 245, 75, 260, 45, 275, 75, 285, 60]
            cvs.create_line(*pts_pr1, width=4, fill="#0055FF")
            cvs.create_text(238, 30, text="R1 (Branch 1)", font=("Helvetica", 12, "bold"), fill="#0055FF")
            cvs.create_line(285, 60, 360, 60, width=4, fill="#000000")
            
            cvs.create_line(140, 150, 190, 150, width=4, fill="#000000")
            pts_pr2 = [190, 150, 200, 135, 215, 165, 230, 135, 245, 165, 260, 135, 275, 165, 285, 150]
            cvs.create_line(*pts_pr2, width=4, fill="#FF3333")
            cvs.create_text(238, 182, text="R2 (Branch 2)", font=("Helvetica", 12, "bold"), fill="#FF3333")
            cvs.create_line(285, 150, 360, 150, width=4, fill="#000000")
            
            cvs.create_line(360, 60, 360, 150, width=4, fill="#000000")
            cvs.create_oval(354, 99, 366, 111, fill="#000000")
            cvs.create_line(360, 105, 480, 105, width=4, fill="#000000")
            cvs.create_text(60, 80, text="IN (+)", font=("Helvetica", 11, "bold"), fill="#000000")
            cvs.create_text(480, 80, text="OUT (-)", font=("Helvetica", 11, "bold"), fill="#000000")

        box = ctk.CTkFrame(self.equiv_container, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        f_in = ctk.CTkFrame(box, fg_color="transparent")
        f_in.pack(pady=5)
        
        ctk.CTkLabel(f_in, text="Resistor Values (Ω, space-separated):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=5, pady=5)
        self.ent_res = ctk.CTkEntry(f_in, width=220, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=4, corner_radius=0)
        self.ent_res.grid(row=0, column=1, padx=5, pady=5)
        self.ent_res.insert(0, "100 220 330")
        
        ctk.CTkLabel(f_in, text="Input Voltage Vin (V):", font=RETRO_FONT, text_color="#000000").grid(row=1, column=0, padx=5, pady=5)
        self.ent_vin = ctk.CTkEntry(f_in, width=100, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=4, corner_radius=0)
        self.ent_vin.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.ent_vin.insert(0, "12")
        
        btn = ctk.CTkButton(box, text=f"Calculate & Plot {mode} Circuit Distribution", font=RETRO_FONT, fg_color="#FF69B4", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=self.calc_equiv)
        btn.pack(pady=10)
        
        res = ctk.CTkFrame(box, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res.pack(fill="x", padx=20, pady=10)
        self.lbl_req = ctk.CTkLabel(res, text="> Req =", font=RETRO_FONT, text_color="#FFBD2E", justify="left")
        self.lbl_req.pack(padx=10, pady=10, anchor="w")

        self.equiv_plot_frame = ctk.CTkFrame(self.equiv_container, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.equiv_plot_frame.pack(fill="x", padx=20, pady=10)
        self.calc_equiv()

    def calc_equiv(self):
        """
        Calculates equivalent resistance, branch/loop currents, and power dissipation
        for Series and Parallel resistor networks.
        
        Engineering Theory:
          - Series Network:
              Req = R1 + R2 + ... + Rn
              Itotal = Vin / Req  (Common current flows through every element)
              V_k = Itotal * R_k  (Voltage divides proportionally to resistance)
              P_k = Itotal^2 * R_k
          - Parallel Network:
              Geq = 1/R1 + 1/R2 + ... + 1/Rn
              Req = 1 / Geq
              I_k = Vin / R_k     (Current divides inversely proportional to resistance)
              Itotal = sum(I_k)
              P_k = Vin^2 / R_k
              
        MATLAB Backend:
          Dispatches to `matlab_manager.ee_series_res` or `matlab_manager.ee_parallel_res`.
        """
        try:
            mode = self.equiv_mode.get()
            # Parse user space-separated resistance values into a numeric list
            vals = [float(x) for x in self.ent_res.get().split() if x.strip()]
            vin = float(self.ent_vin.get().strip())
            
            if not vals: raise ValueError("Enter at least one resistor value.")
            for r in vals:
                if r <= 0: raise ValueError("Resistors must be positive values > 0 Ω")
                
            if mode == "Series":
                # Compute series network via MATLAB Engine backend
                req, itot, v_drops, p_drops, ptot = matlab_manager.ee_series_res(vals, vin)
                res_txt = (
                    f"> Equivalent Resistance (Req) = {req:.3f} Ω\n"
                    f"> Total Loop Current (Itot)    = {itot*1000:.2f} mA\n"
                    f"> Total Power Dissipation      = {ptot:.3f} W\n"
                    f"> Voltage Drops: " + ", ".join([f"V_R{i+1}={v:.2f}V" for i, v in enumerate(v_drops)]) + "\n"
                    f"{matlab_manager.get_status_text()}"
                )
            else:
                # Compute parallel network via MATLAB Engine backend
                req, itot, i_branches, p_drops, ptot = matlab_manager.ee_parallel_res(vals, vin)
                res_txt = (
                    f"> Equivalent Resistance (Req) = {req:.3f} Ω\n"
                    f"> Total Line Current (Itot)    = {itot*1000:.2f} mA\n"
                    f"> Total Power Dissipation      = {ptot:.3f} W\n"
                    f"> Branch Currents: " + ", ".join([f"I_R{i+1}={ib*1000:.1f}mA" for i, ib in enumerate(i_branches)]) + "\n"
                    f"{matlab_manager.get_status_text()}"
                )


            
            self.lbl_req.configure(text=res_txt, text_color="#27C93F")
            self.calc_history_log += f"\n[SERIES/PARALLEL RESISTORS - {mode.upper()}]\n{res_txt}\nTimestamp: {datetime.datetime.now()}\n"
            
            # Dynamic Bar Chart
            for w in self.equiv_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.2, 2.7), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            
            ax1 = fig.add_subplot(121)
            ax1.set_facecolor("#FFFFFF")
            labels = [f"R{i+1}\n({r}Ω)" for i, r in enumerate(vals)]
            x_pos = np.arange(len(labels))
            
            if mode == "Series":
                bars1 = ax1.bar(x_pos, v_drops, color="#0055FF", edgecolor="#000000", lw=2)
                ax1.set_title("Voltage Drop per Resistor", fontsize=10, fontweight="bold")
                ax1.set_ylabel("Voltage V (V)", fontsize=9, fontweight="bold")
            else:
                bars1 = ax1.bar(x_pos, [ib*1000 for ib in i_branches], color="#0055FF", edgecolor="#000000", lw=2)
                ax1.set_title("Branch Current (mA)", fontsize=10, fontweight="bold")
                ax1.set_ylabel("Current (mA)", fontsize=9, fontweight="bold")
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(labels, fontsize=8)
            ax1.grid(True, linestyle=":", alpha=0.6)
            
            ax2 = fig.add_subplot(122)
            ax2.set_facecolor("#FFFFFF")
            bars2 = ax2.bar(x_pos, p_drops, color="#FFBD2E", edgecolor="#000000", lw=2)
            ax2.set_title("Power Dissipation per Resistor", fontsize=10, fontweight="bold")
            ax2.set_ylabel("Power P (W)", fontsize=9, fontweight="bold")
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(labels, fontsize=8)
            ax2.grid(True, linestyle=":", alpha=0.6)
            
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.equiv_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_req.configure(text=f"> ERR: {str(e)}", text_color="#FF5F56")

    def show_kirchhoff(self):
        self.clear_content()
        self.create_retro_title("3. KIRCHHOFF'S LAWS (KVL/KCL MATRIX) 🔋")
        self.create_toolbar(reset_cmd=self.reset_kvl)
        
        self.kvl_mode = ctk.StringVar(value="2 Loops")
        mode_combo = ctk.CTkComboBox(
            self.content_frame, 
            values=["2 Loops", "3 Loops", "4 Loops"], 
            variable=self.kvl_mode, 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            command=self.update_kvl_ui
        )
        mode_combo.pack(pady=5)

        self.kvl_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.kvl_container.pack(fill="both", expand=True)
        self.update_kvl_ui()

    def reset_kvl(self):
        self.update_kvl_ui()

    def update_kvl_ui(self, choice=None):
        for widget in self.kvl_container.winfo_children():
            widget.destroy()
            
        mode = self.kvl_mode.get()
        loops = int(mode.split()[0])
        
        box = ctk.CTkFrame(self.kvl_container, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        cvs_width = 80 + loops * 140 + 80
        cvs = ctk.CTkCanvas(box, width=cvs_width, height=230, bg="#FFF5EE", highlightthickness=4, highlightbackground="#000000")
        cvs.pack(pady=10)
        
        y_top = 40
        y_bot = 180
        x_start = 60
        x_end = x_start + loops * 140
        cvs.create_line(x_start, y_bot, x_end, y_bot, width=4, fill="#000000")
        
        # V1 Battery
        cvs.create_line(x_start, y_bot, x_start, 125, width=4, fill="#000000")
        cvs.create_line(x_start-25, 100, x_start+25, 100, width=4, fill="#000000")
        cvs.create_line(x_start-14, 120, x_start+14, 120, width=6, fill="#000000")
        cvs.create_line(x_start, 100, x_start, y_top, width=4, fill="#000000")
        cvs.create_text(x_start-38, 100, text="+", font=("Helvetica", 14, "bold"), fill="#FF3333")
        cvs.create_text(x_start-38, 120, text="-", font=("Helvetica", 14, "bold"), fill="#000000")
        cvs.create_text(x_start-38, 140, text="V1", font=("Helvetica", 13, "bold"), fill="#FF3333")
        
        # V2 Battery
        cvs.create_line(x_end, y_bot, x_end, 125, width=4, fill="#000000")
        cvs.create_line(x_end-25, 100, x_end+25, 100, width=4, fill="#000000")
        cvs.create_line(x_end-14, 120, x_end+14, 120, width=6, fill="#000000")
        cvs.create_line(x_end, 100, x_end, y_top, width=4, fill="#000000")
        cvs.create_text(x_end+38, 100, text="+", font=("Helvetica", 14, "bold"), fill="#FF3333")
        cvs.create_text(x_end+38, 120, text="-", font=("Helvetica", 14, "bold"), fill="#000000")
        cvs.create_text(x_end+38, 140, text="V2", font=("Helvetica", 13, "bold"), fill="#FF3333")
        
        # Top branch resistors
        for i in range(loops):
            x1 = x_start + i * 140
            x2 = x_start + (i + 1) * 140
            cvs.create_line(x1, y_top, x1+40, y_top, width=4, fill="#000000")
            cvs.create_line(x2-40, y_top, x2, y_top, width=4, fill="#000000")
            cx = (x1 + x2) // 2
            pts_top = [
                x1+40, y_top,
                cx-20, y_top-15,
                cx-10, y_top+15,
                cx, y_top-15,
                cx+10, y_top+15,
                cx+20, y_top-15,
                x2-40, y_top
            ]
            cvs.create_line(*pts_top, width=4, fill="#0055FF")
            cvs.create_text(cx, y_top-24, text=f"R{i+1}", font=("Helvetica", 13, "bold"), fill="#0055FF")
            
            # Loop current arc indicator
            cvs.create_arc(cx-30, 90, cx+30, 150, start=30, extent=280, style="arc", width=3, outline="#27C93F")
            cvs.create_text(cx, 120, text=f"Loop {i+1}\n(I{i+1})", font=("Helvetica", 11, "bold"), fill="#27C93F")
            
        # Middle vertical resistors
        for i in range(loops - 1):
            x = x_start + (i + 1) * 140
            cvs.create_line(x, y_top, x, 75, width=4, fill="#000000")
            cvs.create_line(x, 145, x, y_bot, width=4, fill="#000000")
            pts_vert = [
                x, 75,
                x-12, 85,
                x+12, 97,
                x-12, 109,
                x+12, 121,
                x-12, 133,
                x, 145
            ]
            cvs.create_line(*pts_vert, width=4, fill="#FF69B4")
            cvs.create_text(x+35, 110, text=f"R{loops + i + 1}", font=("Helvetica", 13, "bold"), fill="#FF69B4")

        input_frame = ctk.CTkFrame(box, fg_color="transparent")
        input_frame.pack(pady=10)
        
        self.kvl_entries = {}
        def add_entry(parent, label, row, col, default="10"):
            ctk.CTkLabel(parent, text=label+":", font=RETRO_FONT, text_color="#000000").grid(row=row, column=col*2, padx=5, pady=5, sticky="e")
            ent = ctk.CTkEntry(parent, width=65, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=4, corner_radius=0)
            ent.grid(row=row, column=col*2+1, padx=5, pady=5, sticky="w")
            ent.insert(0, default)
            self.kvl_entries[label] = ent

        add_entry(input_frame, "V1", 0, 0, "12")
        add_entry(input_frame, "V2", 0, 1, "6")
        
        for i in range(loops):
            add_entry(input_frame, f"R{i+1}", 1, i, "2")
            
        for i in range(loops-1):
            add_entry(input_frame, f"R{loops + i + 1}", 2, i, "4")
            
        btn = ctk.CTkButton(box, text="Solve KVL Currents & Matrix Plot", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=self.calc_kvl)
        btn.pack(pady=10)
        
        res = ctk.CTkFrame(box, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res.pack(fill="x", padx=20, pady=10)
        
        self.lbl_kvl = ctk.CTkLabel(res, text="> Results...", font=RETRO_FONT, text_color="#27C93F", justify="left")
        self.lbl_kvl.pack(padx=10, pady=10, anchor="w")

        self.kvl_plot_frame = ctk.CTkFrame(self.kvl_container, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.kvl_plot_frame.pack(fill="x", padx=20, pady=10)
        self.calc_kvl()

    def calc_kvl(self):
        r"""
        Solves multi-loop Kirchhoff's Voltage Law (KVL) mesh networks using matrix algebra.
        
        Engineering Theory:
          - Sum of voltage rises and drops around any closed loop must equal zero: sum(V) = 0.
          - System matrix equation: [R_mesh] * [I_loop] = [V_sources]
              * Diagonal terms A[i, i]: Total self-resistance belonging to mesh i.
              * Off-diagonal terms A[i, j]: Mutual negative resistance shared between mesh i and mesh j.
              * Vector B[i]: Net electromotive force (EMF) driving clockwise current in mesh i.
          - Solved using MATLAB's native linear equation solver: I = A \ B (mldivide).
        """
        try:
            mode = self.kvl_mode.get()
            loops = int(mode.split()[0])
            
            # Read supply voltages V1 and V2
            V1 = float(self.kvl_entries["V1"].get())
            V2 = float(self.kvl_entries["V2"].get())
            
            # Read outer loop resistors and shared middle resistors
            R = [float(self.kvl_entries[f"R{i+1}"].get()) for i in range(loops)]
            R_mid = [float(self.kvl_entries[f"R{loops + i + 1}"].get()) for i in range(loops-1)]
            
            # Solve Kirchhoff loop currents via MATLAB Engine backend (ee_calc.m)
            I = matlab_manager.ee_kvl_solve(loops, V1, V2, R, R_mid)
            
            res_text = f"> SOLVED LOOP CURRENTS (KVL MESH [R][I]=[V]):\n"
            for i in range(loops):
                res_text += f"> Loop {i+1} Current (I{i+1}) = {I[i]:.4f} A ({I[i]*1000:.1f} mA)\n"
            res_text += f"{matlab_manager.get_status_text()}"


                
            self.lbl_kvl.configure(text=res_text.strip(), text_color="#27C93F")
            self.calc_history_log += f"\n[KIRCHHOFF KVL MATRIX SOLVER ({loops} LOOPS)]\n{res_text}\nTimestamp: {datetime.datetime.now()}\n"
            
            # Dynamic Bar Chart
            for w in self.kvl_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.0, 2.5), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#FFFFFF")
            
            labels = [f"Loop {i+1}" for i in range(loops)]
            colors = ["#0055FF", "#27C93F", "#FFBD2E", "#FF3333"][:loops]
            bars = ax.bar(labels, I, color=colors, edgecolor="#000000", lw=2)
            ax.axhline(0, color="#000000", lw=1.5)
            ax.set_title("Solved Kirchhoff Loop Currents", fontsize=11, fontweight="bold")
            ax.set_ylabel("Current (Amperes)", fontsize=9, fontweight="bold")
            ax.grid(True, linestyle=":", alpha=0.6)
            
            for bar in bars:
                height = bar.get_height()
                offset = 0.05 if height >= 0 else -0.15
                ax.annotate(f"{height:.3f}A",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3 if height >= 0 else -12),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight="bold")
                            
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.kvl_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_kvl.configure(text=f"> ERR: {str(e)}", text_color="#FF5F56")

    def show_ac_rlc(self):
        self.clear_content()
        self.create_retro_title("4. AC RLC & POWER FACTOR WAVEFORMS 🌊")
        from practical_applications import get_practical_example
        ctk.CTkLabel(self.content_frame, text=get_practical_example('ac_rlc'), font=('Helvetica', 11, 'italic'), text_color='#333333', wraplength=500, justify='left').pack(pady=(0, 10), padx=20)
        self.create_toolbar(reset_cmd=self.reset_ac_rlc)
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(box, text="AC Series R-L-C Circuit Parameters:", font=RETRO_FONT, text_color="#000000").pack(pady=5)
        
        f = ctk.CTkFrame(box, fg_color="transparent")
        f.pack(pady=5)
        
        self.rlc_entries = {}
        fields = [
            ("Vm Peak (V):", "120"),
            ("Frequency (Hz):", "60"),
            ("Resistor R (Ω):", "50"),
            ("Inductor L (mH):", "150"),
            ("Capacitor C (µF):", "47")
        ]
        
        for i, (lbl, default) in enumerate(fields):
            ctk.CTkLabel(f, text=lbl, font=RETRO_FONT, text_color="#000000").grid(row=i//3, column=(i%3)*2, padx=6, pady=5, sticky="e")
            e = ctk.CTkEntry(f, width=75, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0)
            e.grid(row=i//3, column=(i%3)*2+1, padx=6, pady=5, sticky="w")
            e.insert(0, default)
            self.rlc_entries[lbl] = e
            
        btn = ctk.CTkButton(box, text="Analyze AC Impedance & Render Waveforms", font=RETRO_FONT, fg_color="#0055FF", text_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0, hover_color="#27C93F", command=self.calc_ac_rlc)
        btn.pack(pady=10)
        
        res = ctk.CTkFrame(box, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res.pack(fill="x", padx=20, pady=10)
        
        self.lbl_rlc_res = ctk.CTkLabel(res, text="> Results...", font=RETRO_FONT, text_color="#27C93F", justify="left")
        self.lbl_rlc_res.pack(padx=10, pady=10, anchor="w")

        self.rlc_plot_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.rlc_plot_frame.pack(fill="x", padx=20, pady=10)
        self.calc_ac_rlc()

    def reset_ac_rlc(self):
        defaults = {"Vm Peak (V):": "120", "Frequency (Hz):": "60", "Resistor R (Ω):": "50", "Inductor L (mH):": "150", "Capacitor C (µF):": "47"}
        for k, e in self.rlc_entries.items():
            e.delete(0, "end")
            e.insert(0, defaults[k])
        self.calc_ac_rlc()

    def calc_ac_rlc(self):
        """
        Analyzes steady-state alternating current (AC) series R-L-C circuits.
        
        Engineering Theory:
          - Angular frequency: omega = 2 * pi * f (rad/s)
          - Inductive reactance: XL = omega * L (voltage leads current by 90 deg)
          - Capacitive reactance: XC = 1 / (omega * C) (current leads voltage by 90 deg)
          - Net reactance: Xnet = XL - XC
          - Total complex impedance: Z = R + j*(XL - XC)
          - Impedance magnitude: |Z| = sqrt(R^2 + Xnet^2)
          - Phase angle: phi = atan2(Xnet, R)
          - Power factor: cos(phi) (Lagging if XL > XC, Leading if XC > XL)
          - Real Power (Watts): P = Vrms * Irms * cos(phi)
          - Reactive Power (VAR): Q = Vrms * Irms * sin(phi)
          - Apparent Power (VA): S = Vrms * Irms
        
        MATLAB Backend:
          Dispatches to `matlab_manager.ee_ac_rlc(Vm, freq, R, L, C)` in ee_calc.m.
        """
        try:
            Vm = float(self.rlc_entries["Vm Peak (V):"].get())
            freq = float(self.rlc_entries["Frequency (Hz):"].get())
            R = float(self.rlc_entries["Resistor R (Ω):"].get())
            L = float(self.rlc_entries["Inductor L (mH):"].get()) * 1e-3
            C = float(self.rlc_entries["Capacitor C (µF):"].get()) * 1e-6
            
            if freq <= 0: raise ValueError("Frequency must be > 0 Hz")
            if R <= 0: raise ValueError("Resistance must be > 0 Ω")
            
            # Solve AC impedance and power using MATLAB Engine
            ac_res = matlab_manager.ee_ac_rlc(Vm, freq, R, L, C)
            omega = ac_res['omega']
            X_L = ac_res['XL']
            X_C = ac_res['XC']
            X_net = ac_res['Xnet']
            Z_mag = ac_res['Zmag']
            phase_rad = ac_res['phase_rad']
            phase_deg = ac_res['phase_deg']
            Im = ac_res['Im']
            Vrms = ac_res['Vrms']
            Irms = ac_res['Irms']
            pf = ac_res['pf']
            P_real = ac_res['Preal']
            Q_react = ac_res['Qreact']
            S_app = ac_res['Sapp']
            
            pf_nature = "Lagging (Inductive)" if phase_deg > 0 else ("Leading (Capacitive)" if phase_deg < 0 else "Unity (Resonant)")
            
            res_txt = (
                f"> Reactance: XL = {X_L:.2f} Ω, XC = {X_C:.2f} Ω (Xnet = {X_net:.2f} Ω)\n"
                f"> Impedance: |Z| = {Z_mag:.2f} Ω  ∠{phase_deg:.2f}°\n"
                f"> Peak Current (Im) = {Im:.3f} A ({Im*1000:.1f} mA) | Irms = {Irms:.3f} A\n"
                f"> Power Factor (cos φ) = {pf:.4f} [{pf_nature}]\n"
                f"> Real Power (P) = {P_real:.2f} W | Reactive Power (Q) = {Q_react:.2f} VAR\n"
                f"> Apparent Power (S) = {S_app:.2f} VA\n"
                f"{matlab_manager.get_status_text()}"
            )


            self.lbl_rlc_res.configure(text=res_txt, text_color="#27C93F")
            self.calc_history_log += f"\n[AC RLC CIRCUIT ANALYSIS]\n{res_txt}\nTimestamp: {datetime.datetime.now()}\n"
            
            # Dynamic Waveform Plot
            for w in self.rlc_plot_frame.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(6.2, 3.0), dpi=100)
            fig.patch.set_facecolor("#FFF5EE")
            
            ax1 = fig.add_subplot(211)
            ax1.set_facecolor("#FFFFFF")
            
            T = 1.0 / freq
            t = np.linspace(0, 2*T, 500)
            v_wave = Vm * np.sin(omega * t)
            i_wave = Im * np.sin(omega * t - phase_rad)
            
            ax1.plot(t*1000, v_wave, color="#0055FF", lw=2.5, label=f"v(t) [Vm={Vm:.0f}V]")
            ax1.set_title("AC Steady-State Voltage & Current Waveforms", fontsize=10, fontweight="bold")
            ax1.set_ylabel("Voltage (V)", fontsize=8, fontweight="bold", color="#0055FF")
            ax1.grid(True, linestyle=":", alpha=0.6)
            
            ax1_twin = ax1.twinx()
            ax1_twin.plot(t*1000, i_wave*1000, color="#27C93F", lw=2.5, linestyle="--", label=f"i(t) [Im={Im*1000:.0f}mA]")
            ax1_twin.set_ylabel("Current (mA)", fontsize=8, fontweight="bold", color="#27C93F")
            
            ax2 = fig.add_subplot(212)
            ax2.set_facecolor("#FFFFFF")
            p_wave = v_wave * i_wave
            ax2.plot(t*1000, p_wave, color="#FF3333", lw=2, label="Instantaneous Power p(t)")
            ax2.axhline(P_real, color="#000000", lw=2, linestyle=":", label=f"Average Real Power P={P_real:.1f}W")
            ax2.set_title("Instantaneous Power Waveform p(t) = v(t)·i(t)", fontsize=10, fontweight="bold")
            ax2.set_xlabel("Time (milliseconds)", fontsize=8, fontweight="bold")
            ax2.set_ylabel("Power (W)", fontsize=8, fontweight="bold")
            ax2.grid(True, linestyle=":", alpha=0.6)
            ax2.legend(fontsize=7, loc="upper right")
            
            fig.tight_layout()
            cvs_widget = FigureCanvasTkAgg(fig, master=self.rlc_plot_frame)
            cvs_widget.draw()
            cvs_widget.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            
        except Exception as e:
            self.lbl_rlc_res.configure(text=f"> ERR: {str(e)}", text_color="#FF5F56")
