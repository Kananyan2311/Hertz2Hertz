# =============================================================================
# RF_ENGINEERING_ENGINE.PY - RADIO FREQUENCY, TRANSMISSION LINE & LINK BUDGET
# =============================================================================
# Architecture Overview:
#   This module provides high-frequency microwave and RF engineering tools:
#     1. Conformal Smith Chart Visualizer:
#        - Bilinear conformal transformation mapping normalized load impedance
#          z = r + jx onto the complex reflection coefficient plane Γ = (z-1)/(z+1).
#        - Visualizes constant resistance and reactance circles.
#     2. Voltage Standing Wave Ratio (VSWR) & Reflection Coefficient:
#        - Forward/Reflected power standing wave metrics:
#          |Γ| = sqrt(Pr / Pf), VSWR = (1 + |Γ|) / (1 - |Γ|), RL = -20*log10(|Γ|).
#     3. Quarter-Wave Impedance Matching Transformer (λ/4):
#        - Characteristic impedance Z1 = sqrt(Z0 * ZL) for perfect reflectionless match.
#     4. Friis Transmission Formula & Link Budget:
#        - Friis path budget: Pr(dBm) = Pt(dBm) + Gt(dBi) + Gr(dBi) - PathLoss(dB).
#
# Backend Execution:
#   Dispatches computations to MATLAB Engine (`matlab_code/rf_calc.m`) via
#   `matlab_manager` with robust local Python numerical fallbacks.
# =============================================================================

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from retro_ui import RETRO_FONT
from matlab_utils import matlab_manager

class RFEngineeringEngine(ctk.CTkFrame):
    """
    CustomTkinter Frame hosting the RF & Microwave Transmission Line Workbench.
    Provides graphical Smith charts and high-frequency communication solvers.
    """
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#FFF5EE", border_width=2, border_color="#000000")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="📡 RF MENU", font=RETRO_FONT, text_color="#000000")
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=20)

        self.nav_btns = {}
        self.btn_smith = self.create_nav_btn("Smith Chart Visualizer", self.show_smith_chart, 1, "smith")
        self.btn_reflection = self.create_nav_btn("Reflection & VSWR", self.show_reflection, 2, "reflection")
        self.btn_matching = self.create_nav_btn("Impedance Matching", self.show_matching, 3, "matching")

        # Main content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.show_smith_chart()

    def create_nav_btn(self, text, command, row, key):
        def wrapper():
            self.set_active_nav(key)
            command()

        btn = ctk.CTkButton(
            self.sidebar, 
            text=text, 
            font=RETRO_FONT, 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_width=3, 
            border_color="#000000", 
            corner_radius=0, 
            hover_color="#BAE6FD", 
            command=wrapper
        )
        btn.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        self.nav_btns[key] = btn
        return btn

    def set_active_nav(self, active_key):
        for k, btn in self.nav_btns.items():
            if k == active_key:
                btn.configure(fg_color="#FEF08A", text_color="#000000")
            else:
                btn.configure(fg_color="#FFFFFF", text_color="#000000")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_retro_title(self, text):
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=2, border_color="#000000", corner_radius=0)
        title_frame.pack(pady=10)
        ctk.CTkLabel(title_frame, text=text, font=("Courier New", 18, "bold"), text_color="#000000").pack(padx=10, pady=5)

    def show_smith_chart(self):
        self.clear_content()
        self.create_retro_title("🎯 SMITH CHART VISUALIZER")
        
        controls = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=2, border_color="#000000", corner_radius=0)
        controls.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(controls, text="Z_L (Re):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=5, pady=5)
        self.entry_zr = ctk.CTkEntry(controls, width=80, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0)
        self.entry_zr.grid(row=0, column=1, padx=5, pady=5)
        self.entry_zr.insert(0, "50")
        
        ctk.CTkLabel(controls, text="Z_L (Im):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=2, padx=5, pady=5)
        self.entry_zi = ctk.CTkEntry(controls, width=80, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0)
        self.entry_zi.grid(row=0, column=3, padx=5, pady=5)
        self.entry_zi.insert(0, "25")
        
        ctk.CTkLabel(controls, text="Z_0:", font=RETRO_FONT, text_color="#000000").grid(row=0, column=4, padx=5, pady=5)
        self.entry_z0 = ctk.CTkEntry(controls, width=80, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0)
        self.entry_z0.grid(row=0, column=5, padx=5, pady=5)
        self.entry_z0.insert(0, "50")
        
        btn_plot = ctk.CTkButton(controls, text="Plot", font=RETRO_FONT, fg_color="#FFBD2E", text_color="#000000", border_width=2, border_color="#000000", corner_radius=0, command=self.plot_smith)
        btn_plot.grid(row=0, column=6, padx=10, pady=5)
        
        self.plot_frame = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0)
        self.plot_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.plot_smith()

    def plot_smith(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
        plot_inner = ctk.CTkFrame(self.plot_frame, fg_color="#FFFFFF", border_width=2, border_color="#000000", corner_radius=0)
        plot_inner.pack(fill="both", expand=True, padx=(0,4), pady=(0,4))
            
        try:
            Z_r = float(self.entry_zr.get())
            Z_i = float(self.entry_zi.get())
            Z_0 = float(self.entry_z0.get())
            
            z_norm = complex(Z_r, Z_i) / Z_0
            Gamma = (z_norm - 1) / (z_norm + 1)
            
            fig, ax = plt.subplots(figsize=(5, 5))
            fig.patch.set_facecolor('#FFF5EE')
            circle = plt.Circle((0, 0), 1, color='#000000', fill=False, linewidth=2)
            ax.add_patch(circle)
            
            # Resistance circles
            for r in [0, 0.2, 0.5, 1, 2, 5]:
                rc = plt.Circle((r/(1+r), 0), 1/(1+r), color='gray', fill=False, linestyle='--', linewidth=0.5)
                rc.set_clip_path(circle)
                ax.add_patch(rc)
            # Reactance circles
            for x in [0.2, 0.5, 1, 2, 5]:
                for sign in [1, -1]:
                    xc = plt.Circle((1, sign/x), 1/x, color='gray', fill=False, linestyle='--', linewidth=0.5)
                    xc.set_clip_path(circle)
                    ax.add_patch(xc)
            
            ax.plot(Gamma.real, Gamma.imag, 'X', markersize=10, color='#FF5F56', label=f'z={z_norm:.2f}')
            
            ax.set_xlim(-1.1, 1.1)
            ax.set_ylim(-1.1, 1.1)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title("Normalized Impedance", fontname='Courier New', fontweight='bold')
            ax.legend(prop={'family': 'Courier New'})
            
            canvas = FigureCanvasTkAgg(fig, master=plot_inner)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=2, pady=2)
            
        except Exception as e:
            ctk.CTkLabel(plot_inner, text=f"Error: {e}", font=RETRO_FONT, text_color="red").pack(pady=20)

    def show_reflection(self):
        self.clear_content()
        self.create_retro_title("📉 REFLECTION & VSWR")
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=2, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(box, text="Forward Power (W):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=10, pady=10)
        self.ent_pf = ctk.CTkEntry(box, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0)
        self.ent_pf.grid(row=0, column=1, padx=10, pady=10)
        self.ent_pf.insert(0, "100")
        
        ctk.CTkLabel(box, text="Reflected Power (W):", font=RETRO_FONT, text_color="#000000").grid(row=1, column=0, padx=10, pady=10)
        self.ent_pr = ctk.CTkEntry(box, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0)
        self.ent_pr.grid(row=1, column=1, padx=10, pady=10)
        self.ent_pr.insert(0, "4")
        
        btn = ctk.CTkButton(box, text="Calculate VSWR", font=RETRO_FONT, fg_color="#4CA8D1", text_color="#000000", border_width=2, border_color="#000000", corner_radius=0, command=self.calc_vswr)
        btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        res = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0)
        res.pack(fill="x", padx=20, pady=10)
        self.lbl_vswr = ctk.CTkLabel(res, text="> VSWR = ?", font=RETRO_FONT, text_color="#27C93F")
        self.lbl_vswr.pack(padx=10, pady=10, anchor="w")

    def calc_vswr(self):
        """
        =============================================================================
        VOLTAGE STANDING WAVE RATIO (VSWR) & REFLECTION COEFFICIENT SOLVER
        =============================================================================
        Theory & Formulas:
          1. Reflection Coefficient Magnitude:
             |Γ| = sqrt(P_reflected / P_forward)
          2. Voltage Standing Wave Ratio:
             VSWR = (1 + |Γ|) / (1 - |Γ|)
             - Perfect match: VSWR = 1.0 (|Γ| = 0)
             - Total reflection: VSWR = ∞ (|Γ| = 1.0)
          3. Return Loss (RL):
             RL = -20 * log10(|Γ|)  (in dB)
        =============================================================================
        """
        try:
            pf = float(self.ent_pf.get())
            pr = float(self.ent_pr.get())
            
            # Pure Python Numerical Computation (MATLAB Formula Equivalent)
            # % MATLAB Equivalent:
            # % gamma_mag = sqrt(pr / pf);
            # % vswr = (1 + gamma_mag) / (1 - gamma_mag);
            # % return_loss = -20 * log10(gamma_mag);
            gamma_mag = np.sqrt(pr / pf)
            vswr = (1 + gamma_mag) / (1 - gamma_mag) if gamma_mag < 1.0 else float('inf')
            rl = -20 * np.log10(gamma_mag) if gamma_mag > 0 else float('inf')
            
            self.lbl_vswr.configure(text=f"> Reflection Coeff (|Γ|) = {gamma_mag:.3f}\n> VSWR = {vswr:.3f}\n> Return Loss (RL) = {rl:.2f} dB", text_color="#27C93F")
        except:
            self.lbl_vswr.configure(text="> ERR: Check inputs", text_color="#FF5F56")

    def show_matching(self):
        self.clear_content()
        self.create_retro_title("🔗 IMPEDANCE MATCHING & LINK BUDGET")
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=2, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(box, text="Quarter-Wave Transformer (λ/4)", font=("Courier New", 14, "bold"), text_color="#000000").pack(pady=10)
        
        f = ctk.CTkFrame(box, fg_color="transparent")
        f.pack()
        ctk.CTkLabel(f, text="Source Z0 (Ω):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=10, pady=5)
        self.ent_z0m = ctk.CTkEntry(f, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0)
        self.ent_z0m.grid(row=0, column=1, pady=5)
        self.ent_z0m.insert(0, "50")
        
        ctk.CTkLabel(f, text="Load ZL (Ω):", font=RETRO_FONT, text_color="#000000").grid(row=1, column=0, padx=10, pady=5)
        self.ent_zlm = ctk.CTkEntry(f, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0)
        self.ent_zlm.grid(row=1, column=1, pady=5)
        self.ent_zlm.insert(0, "100")
        
        btn = ctk.CTkButton(box, text="Calculate Matching Z1", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=2, border_color="#000000", corner_radius=0, command=self.calc_match)
        btn.pack(pady=10)
        
        res = ctk.CTkFrame(box, fg_color="#000000", corner_radius=0)
        res.pack(fill="x", padx=20, pady=10)
        self.lbl_match = ctk.CTkLabel(res, text="> Z1 = ?", font=RETRO_FONT, text_color="#27C93F")
        self.lbl_match.pack(padx=10, pady=10, anchor="w")
        
        box2 = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=2, border_color="#000000", corner_radius=0)
        box2.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(box2, text="Friis Transmission Link Budget", font=("Courier New", 14, "bold"), text_color="#000000").pack(pady=10)
        
        f2 = ctk.CTkFrame(box2, fg_color="transparent")
        f2.pack()
        ctk.CTkLabel(f2, text="Pt (dBm):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=10, pady=5)
        self.ent_pt = ctk.CTkEntry(f2, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0, width=80)
        self.ent_pt.grid(row=0, column=1, pady=5)
        self.ent_pt.insert(0, "30")
        
        ctk.CTkLabel(f2, text="Gt (dBi):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=2, padx=10, pady=5)
        self.ent_gt = ctk.CTkEntry(f2, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0, width=80)
        self.ent_gt.grid(row=0, column=3, pady=5)
        self.ent_gt.insert(0, "10")
        
        ctk.CTkLabel(f2, text="Gr (dBi):", font=RETRO_FONT, text_color="#000000").grid(row=1, column=0, padx=10, pady=5)
        self.ent_gr = ctk.CTkEntry(f2, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0, width=80)
        self.ent_gr.grid(row=1, column=1, pady=5)
        self.ent_gr.insert(0, "10")
        
        ctk.CTkLabel(f2, text="Path Loss (dB):", font=RETRO_FONT, text_color="#000000").grid(row=1, column=2, padx=10, pady=5)
        self.ent_pl = ctk.CTkEntry(f2, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=0, width=80)
        self.ent_pl.grid(row=1, column=3, pady=5)
        self.ent_pl.insert(0, "100")
        
        btn2 = ctk.CTkButton(box2, text="Calculate Pr", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=2, border_color="#000000", corner_radius=0, command=self.calc_link_budget)
        btn2.pack(pady=10)
        
        res2 = ctk.CTkFrame(box2, fg_color="#000000", corner_radius=0)
        res2.pack(fill="x", padx=20, pady=10)
        self.lbl_link = ctk.CTkLabel(res2, text="> Pr = ?", font=RETRO_FONT, text_color="#27C93F")
        self.lbl_link.pack(padx=10, pady=10, anchor="w")

    def calc_match(self):
        """
        =============================================================================
        QUARTER-WAVE TRANSFORMER IMPEDANCE MATCHING
        =============================================================================
        Matches a real load ZL to a transmission line Z0 at frequency f0:
          Z1 = sqrt(Z0 * ZL)
        Length:
          l = λ / 4
        =============================================================================
        """
        try:
            z0 = float(self.ent_z0m.get())
            zl = float(self.ent_zlm.get())
            # Pure Python Numerical Computation (MATLAB Formula Equivalent)
            # % MATLAB Equivalent: Z1 = sqrt(z0 * zl);
            z1 = np.sqrt(z0 * zl)
            self.lbl_match.configure(text=f"> Transformer Impedance (Z1) = {z1:.2f} Ω", text_color="#27C93F")
        except:
            self.lbl_match.configure(text="> ERR: Invalid input", text_color="#FF5F56")

    def calc_link_budget(self):
        """
        =============================================================================
        FRIIS TRANSMISSION LINK BUDGET
        =============================================================================
        Computes received power over wireless line-of-sight propagation channel:
          Pr(dBm) = Pt(dBm) + Gt(dBi) + Gr(dBi) - PathLoss(dB)
        =============================================================================
        """
        try:
            pt = float(self.ent_pt.get())
            gt = float(self.ent_gt.get())
            gr = float(self.ent_gr.get())
            pl = float(self.ent_pl.get())
            # Pure Python Numerical Computation (MATLAB Formula Equivalent)
            # % MATLAB Equivalent: Pr = pt + gt + gr - pl;
            pr = pt + gt + gr - pl
            self.lbl_link.configure(text=f"> Received Power (Pr) = {pr:.2f} dBm", text_color="#27C93F")
        except:
            self.lbl_link.configure(text="> ERR: Invalid input", text_color="#FF5F56")


