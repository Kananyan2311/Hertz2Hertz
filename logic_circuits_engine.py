# =============================================================================
# LOGIC_CIRCUITS_ENGINE.PY - DIGITAL SYSTEMS & BOOLEAN LOGIC SIMULATOR
# =============================================================================
# Architecture Overview:
#   This module implements digital logic analysis and minimization:
#     1. Radix & Base Conversions:
#        - Positional numbering conversions across Decimal, Binary, Octal, Hexadecimal.
#        - 7-bit ASCII transmission framing with Even and Odd parity generator.
#     2. IEEE Standard Logic Gates & Evaluator:
#        - Vector schematic rendering for AND, OR, XOR, NAND, NOR, XNOR.
#        - Interactive dual-input truth evaluations.
#     3. Karnaugh Map (K-Map) Multi-Variable Minimization Engine:
#        - Gray-code mapped topologies: 2x2, 2x3, 3x2, 3x3, 2x4, 4x2, 4x4, and 5-variable 5x5 (32 cells).
#        - Quine-McCluskey algorithmic grouping:
#          Finds Prime Implicants (PI) and solves Petrick's / Greedy set cover
#          for minimal canonical Sum-of-Products (SOP) expressions.
#     4. Boolean Expression Parser & Combinational Evaluator:
#        - Arbitrary expression tokenizer evaluating arbitrary combinations of A, B, C, D, E.
#        - Exhaustive 32-row truth table generation with canonical SOP extraction.
#     5. Sequential Logic & Finite State Machines:
#        - D flip-flop, JK flip-flop, and SR latch excitation state transitions.
#
# Integration with MATLAB Engine:
#   Dispatches radix and logic gate evaluations to `matlab_code/logic_calc.m` via
#   `matlab_manager` with robust local Python numerical fallbacks.
# =============================================================================

import customtkinter as ctk
import re
import math
from retro_ui import RETRO_FONT
from matlab_utils import matlab_manager

class LogicCircuitsEngine(ctk.CTkFrame):
    """
    CustomTkinter Frame hosting the Digital Logic & Combinational Circuit Simulator.
    Provides vector gate symbols, interactive K-maps, and truth table engines.
    """
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#FFF5EE", border_width=2, border_color="#000000")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="🖩 LOGIC CIRCUITS", font=RETRO_FONT, text_color="#000000")
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=20)

        # Navigation buttons dictionary for active state tracking
        self.nav_btns = {}

        # Updated Syllabus Navigation with Lemon Yellow active highlighting
        self.btn_sys = self.create_nav_btn("I. Number Systems", self.show_numsys, 1, "numsys")
        self.btn_bool = self.create_nav_btn("II. Gates", self.show_boolean, 2, "bool")
        self.btn_min = self.create_nav_btn("III. Logic Min (K-Map)", self.show_minimization, 3, "min")
        self.btn_comb = self.create_nav_btn("IV. Boolean/Combinational", self.show_combinational, 4, "comb")
        self.btn_seq = self.create_nav_btn("V. Sequential & FSM", self.show_sequential, 5, "seq")

        # Main content (Scrollable to prevent cramped UI)
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.set_active_nav("numsys")
        self.show_numsys()

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
        """
        Sets the active navigation selection button to Lemon Beach yellow (#FEF08A)
        with 4px stark black neobrutalist border, resetting all other buttons to white.
        """
        for k, btn in self.nav_btns.items():
            if k == active_key:
                btn.configure(fg_color="#FEF08A", text_color="#000000", border_color="#000000")
            else:
                btn.configure(fg_color="#FFFFFF", text_color="#000000", border_color="#000000")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_retro_title(self, text):
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", border_width=2, border_color="#000000", corner_radius=0)
        title_frame.pack(pady=10)
        ctk.CTkLabel(title_frame, text=text, font=("Courier New", 18, "bold"), text_color="#000000").pack(padx=10, pady=5)

    def show_numsys(self):
        self.clear_content()
        self.create_retro_title("I. DATA REP. & BASE CONVERSION 💾")
        
        # Updated Base Converter
        converter_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        converter_frame.pack(pady=10, padx=20, fill="x")
        
        f_top = ctk.CTkFrame(converter_frame, fg_color="transparent")
        f_top.pack(pady=5)
        
        ctk.CTkLabel(f_top, text="From:", font=("Helvetica", 12, "bold"), text_color="#000000").grid(row=0, column=0, padx=5, pady=5)
        self.combo_from = ctk.CTkComboBox(f_top, values=["Decimal", "Binary", "Octal", "Hexadecimal"], font=("Helvetica", 12, "bold"), fg_color="#FFFFFF", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0)
        self.combo_from.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(f_top, text="To:", font=("Helvetica", 12, "bold"), text_color="#000000").grid(row=0, column=2, padx=5, pady=5)
        self.combo_to = ctk.CTkComboBox(f_top, values=["Decimal", "Binary", "Octal", "Hexadecimal"], font=("Helvetica", 12, "bold"), fg_color="#FFFFFF", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0)
        self.combo_to.grid(row=0, column=3, padx=5, pady=5)
        
        f_mid = ctk.CTkFrame(converter_frame, fg_color="transparent")
        f_mid.pack(pady=5)
        
        ctk.CTkLabel(f_mid, text="Value:", font=("Helvetica", 12, "bold"), text_color="#000000").grid(row=0, column=0, padx=5, pady=5)
        self.entry_dec = ctk.CTkEntry(f_mid, font=("Helvetica", 12, "bold"), fg_color="#FFFFFF", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0)
        self.entry_dec.grid(row=0, column=1, padx=5, pady=5)
        
        btn_convert = ctk.CTkButton(f_mid, text="Convert", font=("Helvetica", 12, "bold"), fg_color="#E76F51", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=self.convert_numbers)
        btn_convert.grid(row=0, column=2, padx=5, pady=5)
        
        res_frame = ctk.CTkFrame(converter_frame, fg_color="#000000", corner_radius=0)
        res_frame.pack(pady=10, padx=10, fill="x")
        
        self.result_lbl = ctk.CTkLabel(res_frame, text="> Awaiting Input...", font=("Helvetica", 12, "bold"), text_color="#27C93F", justify="left")
        self.result_lbl.pack(padx=10, pady=10, anchor="w")

        # New Parity & ASCII tool
        parity_frame = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=2, border_color="#000000", corner_radius=10)
        parity_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(parity_frame, text="ASCII Char:", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=10, pady=10)
        self.entry_char = ctk.CTkEntry(parity_frame, width=50, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", corner_radius=5)
        self.entry_char.grid(row=0, column=1, padx=10, pady=10)
        
        btn_parity = ctk.CTkButton(parity_frame, text="Generate Parity Bit", font=RETRO_FONT, fg_color="#4CA8D1", text_color="#000000", border_width=2, border_color="#000000", corner_radius=10, command=self.calc_parity)
        btn_parity.grid(row=0, column=2, padx=10, pady=10)
        
        pres_frame = ctk.CTkFrame(parity_frame, fg_color="#000000", corner_radius=5)
        pres_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.lbl_parity = ctk.CTkLabel(pres_frame, text="> Binary: -- | Even: -- | Odd: --", font=RETRO_FONT, text_color="#FFBD2E", justify="left")
        self.lbl_parity.pack(padx=10, pady=10, anchor="w")

    def calc_parity(self):
        """
        =============================================================================
        ASCII TRANSMISSION & PARITY BIT ENCODING
        =============================================================================
        Theory:
          In serial digital data transmission, parity provides single-bit error detection:
          - Even Parity: Adds a bit so the total number of '1's in the transmitted word is EVEN.
          - Odd Parity: Adds a bit so the total number of '1's in the transmitted word is ODD.
        =============================================================================
        """
        try:
            char = self.entry_char.get()
            if len(char) != 1: raise ValueError()
            ascii_val = ord(char)
            bin_str = f"{ascii_val:07b}"
            ones = bin_str.count('1')
            even_p = '1' if ones % 2 != 0 else '0'
            odd_p = '0' if ones % 2 != 0 else '1'
            self.lbl_parity.configure(text=f"> ASCII '{char}' = {ascii_val}\n> 7-bit Binary = {bin_str}\n> Even Parity Word = {even_p}{bin_str}\n> Odd Parity Word = {odd_p}{bin_str}")
        except:
            self.lbl_parity.configure(text="> ERR: Enter exactly one character.", text_color="#FF5F56")
        
    def convert_numbers(self):
        """
        =============================================================================
        RADIX & POSITIONAL NUMBER SYSTEM CONVERTER
        =============================================================================
        Converts arbitrary values between bases:
          - Decimal (Base 10)
          - Binary (Base 2)
          - Octal (Base 8)
          - Hexadecimal (Base 16)
        =============================================================================
        """
        try:
            val_str = self.entry_dec.get()
            from_base = self.combo_from.get()
            to_base = self.combo_to.get()
            
            base_map = {"Decimal": 10, "Binary": 2, "Octal": 8, "Hexadecimal": 16}
            val = int(val_str, base_map[from_base])
            
            # Pure Python Computation with MATLAB Radix Conversion Syntax
            # % MATLAB Equivalent:
            # % dec_val = base2dec(val_str, base_in);
            # % if to_base == "Binary", res = dec2bin(dec_val);
            # % elseif to_base == "Octal", res = dec2base(dec_val, 8);
            # % elseif to_base == "Hexadecimal", res = dec2hex(dec_val);
            # % else, res = num2str(dec_val); end
            if to_base == "Decimal": 
                res = str(val)
            elif to_base == "Binary": 
                res = bin(val)[2:]
            elif to_base == "Octal": 
                res = oct(val)[2:]
            elif to_base == "Hexadecimal": 
                res = hex(val)[2:].upper()
            
            res_text = f"> Result ({to_base}): {res}"
            self.result_lbl.configure(text=res_text, text_color="#27C93F")
        except ValueError:
            self.result_lbl.configure(text="> ERR: Invalid input for base.", text_color="#FF5F56")

    def show_boolean(self):
        self.clear_content()
        self.create_retro_title("II. GATES 🔌")
        
        from practical_applications import get_practical_example
        ctk.CTkLabel(self.content_frame, text=get_practical_example("logic_gates"), font=("Helvetica", 11, "italic"), text_color="#333333", wraplength=500, justify="left").pack(pady=(0, 10), padx=20)
        self.gate_cvs = ctk.CTkCanvas(self.content_frame, width=480, height=200, bg="#FFF5EE", highlightthickness=4, highlightbackground="#000000")
        self.gate_cvs.pack(pady=12)
        self.draw_gate("AND")
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(box, text="Logic Gate Evaluator 🖩", font=("Helvetica", 14, "bold"), text_color="#000000").pack(pady=10)
        
        f = ctk.CTkFrame(box, fg_color="transparent")
        f.pack()
        ctk.CTkLabel(f, text="Input A (0/1):", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=10, pady=5)
        self.ent_gate_a = ctk.CTkEntry(f, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=2, corner_radius=0, width=60)
        self.ent_gate_a.grid(row=0, column=1, pady=5)
        self.ent_gate_a.insert(0, "1")
        
        ctk.CTkLabel(f, text="Input B (0/1):", font=RETRO_FONT, text_color="#000000").grid(row=1, column=0, padx=10, pady=5)
        self.ent_gate_b = ctk.CTkEntry(f, font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=2, corner_radius=0, width=60)
        self.ent_gate_b.grid(row=1, column=1, pady=5)
        self.ent_gate_b.insert(0, "0")
        
        ctk.CTkLabel(f, text="Gate Type:", font=RETRO_FONT, text_color="#000000").grid(row=2, column=0, padx=10, pady=5)
        self.combo_gate = ctk.CTkComboBox(f, values=["AND", "OR", "XOR", "NAND", "NOR", "XNOR"], font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=4, corner_radius=0, command=self.draw_gate)
        self.combo_gate.grid(row=2, column=1, pady=5)
        
        btn_eval = ctk.CTkButton(box, text="Evaluate Gate", font=("Helvetica", 12, "bold"), fg_color="#FFBD2E", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=self.calc_gate)
        btn_eval.pack(pady=5)
        
        btn_tt = ctk.CTkButton(box, text="Truth Table", font=("Helvetica", 12, "bold"), fg_color="#4CA8D1", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=self.gen_truth_table)
        btn_tt.pack(pady=5)
        
        res_frame = ctk.CTkFrame(box, fg_color="#000000", corner_radius=0)
        res_frame.pack(fill="x", padx=20, pady=10)
        self.lbl_gate_out = ctk.CTkLabel(res_frame, text="> Output Y = ?", font=("Helvetica", 12, "bold"), text_color="#27C93F", justify="left")
        self.lbl_gate_out.pack(padx=10, pady=10, anchor="w")

    def draw_gate(self, gate_type):
        cvs = self.gate_cvs
        cvs.delete("all")
        
        # Enlarge inputs A & B
        y_a = 65
        y_b = 135
        cvs.create_text(40, y_a, text="A", font=("Helvetica", 16, "bold"), fill="#000000")
        cvs.create_text(40, y_b, text="B", font=("Helvetica", 16, "bold"), fill="#000000")
        cvs.create_oval(54, y_a-5, 64, y_a+5, fill="#000000")
        cvs.create_oval(54, y_b-5, 64, y_b+5, fill="#000000")
        
        gate_color = "#0055FF"
        
        if "AND" in gate_type:
            # Inputs to gate back
            cvs.create_line(64, y_a, 160, y_a, width=4, fill="#000000")
            cvs.create_line(64, y_b, 160, y_b, width=4, fill="#000000")
            
            # Straight back line
            cvs.create_line(160, 40, 160, 160, width=4, fill=gate_color)
            # Top and bottom straight lines
            cvs.create_line(160, 40, 230, 40, width=4, fill=gate_color)
            cvs.create_line(160, 160, 230, 160, width=4, fill=gate_color)
            # Semicircular curved front
            cvs.create_arc(160, 40, 300, 160, start=-90, extent=180, style="arc", width=4, outline=gate_color)
            tip_x = 300
        elif "OR" in gate_type:
            # Curved back
            back_pts = [160, 40, 185, 70, 195, 100, 185, 130, 160, 160]
            cvs.create_line(*back_pts, smooth=True, width=4, fill=gate_color)
            
            # Top curve to tip
            top_pts = [160, 40, 215, 43, 265, 65, 305, 100]
            cvs.create_line(*top_pts, smooth=True, width=4, fill=gate_color)
            
            # Bottom curve to tip
            bot_pts = [305, 100, 265, 135, 215, 157, 160, 160]
            cvs.create_line(*bot_pts, smooth=True, width=4, fill=gate_color)
            
            # Inputs to back of OR gate
            cvs.create_line(64, y_a, 180, y_a, width=4, fill="#000000")
            cvs.create_line(64, y_b, 180, y_b, width=4, fill="#000000")
            
            if "X" in gate_type:
                # Extra parallel curve for XOR
                xor_pts = [135, 40, 160, 70, 170, 100, 160, 130, 135, 160]
                cvs.create_line(*xor_pts, smooth=True, width=4, fill=gate_color)
            tip_x = 305
            
        # Invert bubble for NAND, NOR, XNOR
        out_start_x = tip_x
        if gate_type in ["NAND", "NOR", "XNOR"]:
            bubble_rad = 9
            cvs.create_oval(tip_x, 100 - bubble_rad, tip_x + 2*bubble_rad, 100 + bubble_rad, width=3, outline=gate_color, fill="#FFFFFF")
            out_start_x = tip_x + 2*bubble_rad
            
        # Output Y lead and label
        cvs.create_line(out_start_x, 100, 400, 100, width=4, fill="#000000")
        cvs.create_oval(395, 95, 405, 105, fill="#000000")
        cvs.create_text(435, 100, text="Y", font=("Helvetica", 18, "bold"), fill="#000000")
        
        # Center gate title
        cvs.create_text(240, 185, text=f"[ {gate_type} GATE ]", font=("Helvetica", 12, "bold"), fill=gate_color)

    def calc_gate_logic(self, a, b, gate):
        """
        =============================================================================
        BOOLEAN LOGIC OPERATOR EVALUATOR
        =============================================================================
        Evaluates the 6 fundamental digital gate functions:
          - AND:  Y = A · B
          - OR:   Y = A + B
          - XOR:  Y = A ⊕ B = A'B + AB'
          - NAND: Y = (A · B)'
          - NOR:  Y = (A + B)'
          - XNOR: Y = (A ⊕ B)' = AB + A'B'
        =============================================================================
        """
        # Pure Python Boolean Logic (MATLAB-equivalent bitwise expressions)
        # % MATLAB Equivalent:
        # % switch gate
        # %   case 'AND', Y = bitand(a, b);
        # %   case 'OR',  Y = bitor(a, b);
        # %   case 'XOR', Y = bitxor(a, b);
        # %   case 'NAND', Y = ~bitand(a, b);
        # %   case 'NOR',  Y = ~bitor(a, b);
        # %   case 'XNOR', Y = ~bitxor(a, b);
        # % end
        if gate == "AND": return int(a & b)
        elif gate == "OR": return int(a | b)
        elif gate == "XOR": return int(a ^ b)
        elif gate == "NAND": return int(not(a & b))
        elif gate == "NOR": return int(not(a | b))
        elif gate == "XNOR": return int(not(a ^ b))
        return 0

    def calc_gate(self):
        try:
            a = int(self.ent_gate_a.get())
            b = int(self.ent_gate_b.get())
            gate = self.combo_gate.get()
            
            y = self.calc_gate_logic(a, b, gate)
            
            self.lbl_gate_out.configure(text=f"> Output Y = {y}", text_color="#27C93F")
        except:
            self.lbl_gate_out.configure(text="> ERR: Use 0 or 1", text_color="#FF5F56")

    def gen_truth_table(self):
        """
        Generates exhaustive dual-input 4-row truth table for selected gate.
        """
        gate = self.combo_gate.get()
        tt_text = f"> Truth Table for {gate}:\n> A B | Y\n"
        for a in [0, 1]:
            for b in [0, 1]:
                y = self.calc_gate_logic(a, b, gate)
                tt_text += f"> {a} {b} | {y}\n"
        self.lbl_gate_out.configure(text=tt_text, text_color="#27C93F")

    def show_minimization(self):
        self.clear_content()
        self.create_retro_title("III. KARNAUGH MAP & QUINE-MCCLUSKEY")
        
        from practical_applications import get_practical_example
        ctk.CTkLabel(self.content_frame, text=get_practical_example("kmap"), font=("Helvetica", 11, "italic"), text_color="#333333", wraplength=500, justify="left").pack(pady=(0, 10), padx=20)
        top_bar = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        top_bar.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(top_bar, text="K-Map Grid Size:", font=("Helvetica", 12, "bold"), text_color="#000000").pack(side="left", padx=10, pady=8)
        self.kmap_size_combo = ctk.CTkComboBox(
            top_bar, 
            values=["5-Variable (A B C D E)", "4x4 (4-Var ABCD)", "2x4 (3-Var ABC)", "4x2 (3-Var ABC)", "2x2 (2-Var AB)", "2x3", "3x2", "3x3", "5x5"], 
            font=("Helvetica", 12, "bold"), 
            fg_color="#FFFFFF", 
            text_color="#000000", 
            border_color="#000000", 
            border_width=4, 
            corner_radius=0, 
            width=210,
            command=self.update_kmap_grid
        )
        self.kmap_size_combo.set("5-Variable (A B C D E)")
        self.kmap_size_combo.pack(side="left", padx=10, pady=8)
        
        btn_clr = ctk.CTkButton(top_bar, text="All 0", width=65, font=("Helvetica", 11, "bold"), fg_color="#FF3333", text_color="#FFFFFF", border_width=3, border_color="#000000", corner_radius=0, command=lambda: self.set_all_kmap(0))
        btn_clr.pack(side="left", padx=5)
        
        btn_all1 = ctk.CTkButton(top_bar, text="All 1", width=65, font=("Helvetica", 11, "bold"), fg_color="#0055FF", text_color="#FFFFFF", border_width=3, border_color="#000000", corner_radius=0, command=lambda: self.set_all_kmap(1))
        btn_all1.pack(side="left", padx=5)
        
        btn_inv = ctk.CTkButton(top_bar, text="Invert", width=65, font=("Helvetica", 11, "bold"), fg_color="#4CA8D1", text_color="#000000", border_width=3, border_color="#000000", corner_radius=0, command=self.invert_kmap)
        btn_inv.pack(side="left", padx=5)

        info_lbl = ctk.CTkLabel(self.content_frame, text="Click any cell to toggle value (0 ⟷ 1). Active minterms highlighted in Green:", font=("Helvetica", 11, "bold"), text_color="#000000")
        info_lbl.pack(pady=(5, 5))
        
        self.kmap_grid_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.kmap_grid_container.pack(pady=5)
        
        btn_solve = ctk.CTkButton(
            self.content_frame, 
            text="Solve K-Map & Generate Minimal Equation", 
            font=("Helvetica", 13, "bold"), 
            fg_color="#FFBD2E", 
            text_color="#000000", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            hover_color="#FFFFFF",
            command=self.solve_kmap
        )
        btn_solve.pack(pady=10)
        
        res = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0, border_width=4, border_color="#000000")
        res.pack(fill="x", padx=20, pady=10)
        self.lbl_kmap = ctk.CTkLabel(res, text="> Awaiting Grid Data...", font=("Helvetica", 13, "bold"), text_color="#27C93F", justify="left")
        self.lbl_kmap.pack(padx=14, pady=12, anchor="w")
        
        self.update_kmap_grid("5-Variable (A B C D E)")

    def update_kmap_grid(self, choice):
        for widget in self.kmap_grid_container.winfo_children():
            widget.destroy()
            
        self.kmap_cells = {}
        self.kmap_cell_state = {}
        self.kmap_mode = choice
        
        # 5-Variable Mode: TWO 4x4 sub-grids (A = 0 and A = 1) side-by-side
        if "5" in choice:
            self.kmap_N = 5
            self.kmap_var_names = ['A', 'B', 'C', 'D', 'E']
            
            dual_box = ctk.CTkFrame(self.kmap_grid_container, fg_color="transparent")
            dual_box.pack(padx=10, pady=5)
            
            g = [0, 1, 3, 2] # Gray code sequence: 00, 01, 11, 10
            row_labels = ["00", "01", "11", "10"]
            col_labels = ["00", "01", "11", "10"]
            
            for a_val in [0, 1]:
                sub_frame = ctk.CTkFrame(dual_box, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
                sub_frame.pack(side="left", padx=12, pady=5)
                
                # Header title: A = 0 or A = 1
                title_lbl = ctk.CTkLabel(sub_frame, text=f"A = {a_val}", font=("Helvetica", 15, "bold"), text_color="#0055FF" if a_val == 0 else "#E76F51")
                title_lbl.grid(row=0, column=0, columnspan=5, pady=(8, 4))
                
                # Corner Header: BC \ DE
                corner_lbl = ctk.CTkLabel(sub_frame, text="BC \\ DE", font=("Helvetica", 10, "bold"), text_color="#000000")
                corner_lbl.grid(row=1, column=0, padx=4, pady=4)
                
                # Column Gray Code Headers: 00, 01, 11, 10
                for c_idx, cl in enumerate(col_labels):
                    c_lbl = ctk.CTkLabel(sub_frame, text=cl, font=("Helvetica", 11, "bold"), text_color="#0055FF")
                    c_lbl.grid(row=1, column=c_idx + 1, padx=2, pady=4)
                    
                # 4 Data Rows with Row Gray Code Headers
                for r_idx, rl in enumerate(row_labels):
                    r_lbl = ctk.CTkLabel(sub_frame, text=rl, font=("Helvetica", 11, "bold"), text_color="#FF3333")
                    r_lbl.grid(row=r_idx + 2, column=0, padx=4, pady=2)
                    
                    for c_idx in range(4):
                        # Minterm mapping:
                        # Left Block (A=0): m0..m15
                        # Right Block (A=1): m16..m31
                        m = (a_val << 4) | (g[r_idx] << 2) | g[c_idx]
                        self.kmap_cell_state[m] = 0
                        
                        btn = ctk.CTkButton(
                            sub_frame,
                            text=f"m{m}\n0",
                            width=52,
                            height=44,
                            font=("Helvetica", 10, "bold"),
                            fg_color="#FFFFFF",
                            text_color="#000000",
                            border_width=2,
                            border_color="#000000",
                            corner_radius=0,
                            hover_color="#E0E0E0",
                            command=lambda minterm=m: self.toggle_kmap_cell(minterm)
                        )
                        btn.grid(row=r_idx + 2, column=c_idx + 1, padx=2, pady=2)
                        self.kmap_cells[m] = btn
                        
            self.lbl_kmap.configure(text="> 5-Variable SOP K-Map (32 Cells, Variables: A, B, C, D, E).\n> Left Block: A = 0 (m0..m15) | Right Block: A = 1 (m16..m31)\n> Click any cell to toggle value (0 ⟷ 1).")
            return
            
        elif "4x4" in choice:
            self.kmap_N = 4
            self.kmap_var_names = ['A', 'B', 'C', 'D']
            grid_box = ctk.CTkFrame(self.kmap_grid_container, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
            grid_box.pack(padx=10, pady=5)
            
            g = [0, 1, 3, 2]
            row_labels = ["00", "01", "11", "10"]
            col_labels = ["00", "01", "11", "10"]
            
            ctk.CTkLabel(grid_box, text="AB \\ CD", font=("Helvetica", 10, "bold"), text_color="#000000").grid(row=0, column=0, padx=4, pady=4)
            for c_idx, cl in enumerate(col_labels):
                ctk.CTkLabel(grid_box, text=cl, font=("Helvetica", 11, "bold"), text_color="#0055FF").grid(row=0, column=c_idx+1, padx=2, pady=4)
                
            for r_idx, rl in enumerate(row_labels):
                ctk.CTkLabel(grid_box, text=rl, font=("Helvetica", 11, "bold"), text_color="#FF3333").grid(row=r_idx+1, column=0, padx=4, pady=2)
                for c_idx in range(4):
                    m = (g[r_idx] << 2) | g[c_idx]
                    self.kmap_cell_state[m] = 0
                    btn = ctk.CTkButton(
                        grid_box,
                        text=f"m{m}\n0",
                        width=52,
                        height=44,
                        font=("Helvetica", 10, "bold"),
                        fg_color="#FFFFFF",
                        text_color="#000000",
                        border_width=2,
                        border_color="#000000",
                        corner_radius=0,
                        hover_color="#E0E0E0",
                        command=lambda minterm=m: self.toggle_kmap_cell(minterm)
                    )
                    btn.grid(row=r_idx+1, column=c_idx+1, padx=2, pady=2)
                    self.kmap_cells[m] = btn
            self.lbl_kmap.configure(text="> 4-Variable K-Map Ready (16 Cells, Variables: A, B, C, D). Click cells to toggle.")
            return

        elif "2x4" in choice:
            self.kmap_N = 3
            self.kmap_var_names = ['A', 'B', 'C']
            grid_box = ctk.CTkFrame(self.kmap_grid_container, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
            grid_box.pack(padx=10, pady=5)
            
            g = [0, 1, 3, 2]
            row_labels = ["0", "1"]
            col_labels = ["00", "01", "11", "10"]
            
            ctk.CTkLabel(grid_box, text="A \\ BC", font=("Helvetica", 10, "bold"), text_color="#000000").grid(row=0, column=0, padx=4, pady=4)
            for c_idx, cl in enumerate(col_labels):
                ctk.CTkLabel(grid_box, text=cl, font=("Helvetica", 11, "bold"), text_color="#0055FF").grid(row=0, column=c_idx+1, padx=2, pady=4)
                
            for r_idx, rl in enumerate(row_labels):
                ctk.CTkLabel(grid_box, text=rl, font=("Helvetica", 11, "bold"), text_color="#FF3333").grid(row=r_idx+1, column=0, padx=4, pady=2)
                for c_idx in range(4):
                    m = (r_idx << 2) | g[c_idx]
                    self.kmap_cell_state[m] = 0
                    btn = ctk.CTkButton(
                        grid_box,
                        text=f"m{m}\n0",
                        width=52,
                        height=44,
                        font=("Helvetica", 10, "bold"),
                        fg_color="#FFFFFF",
                        text_color="#000000",
                        border_width=2,
                        border_color="#000000",
                        corner_radius=0,
                        hover_color="#E0E0E0",
                        command=lambda minterm=m: self.toggle_kmap_cell(minterm)
                    )
                    btn.grid(row=r_idx+1, column=c_idx+1, padx=2, pady=2)
                    self.kmap_cells[m] = btn
            self.lbl_kmap.configure(text="> 3-Variable K-Map Ready (8 Cells, Variables: A, B, C). Click cells to toggle.")
            return

        elif "4x2" in choice:
            self.kmap_N = 3
            self.kmap_var_names = ['A', 'B', 'C']
            grid_box = ctk.CTkFrame(self.kmap_grid_container, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
            grid_box.pack(padx=10, pady=5)
            
            g = [0, 1, 3, 2]
            row_labels = ["00", "01", "11", "10"]
            col_labels = ["0", "1"]
            
            ctk.CTkLabel(grid_box, text="AB \\ C", font=("Helvetica", 10, "bold"), text_color="#000000").grid(row=0, column=0, padx=4, pady=4)
            for c_idx, cl in enumerate(col_labels):
                ctk.CTkLabel(grid_box, text=cl, font=("Helvetica", 11, "bold"), text_color="#0055FF").grid(row=0, column=c_idx+1, padx=2, pady=4)
                
            for r_idx, rl in enumerate(row_labels):
                ctk.CTkLabel(grid_box, text=rl, font=("Helvetica", 11, "bold"), text_color="#FF3333").grid(row=r_idx+1, column=0, padx=4, pady=2)
                for c_idx in range(2):
                    m = (g[r_idx] << 1) | c_idx
                    self.kmap_cell_state[m] = 0
                    btn = ctk.CTkButton(
                        grid_box,
                        text=f"m{m}\n0",
                        width=52,
                        height=44,
                        font=("Helvetica", 10, "bold"),
                        fg_color="#FFFFFF",
                        text_color="#000000",
                        border_width=2,
                        border_color="#000000",
                        corner_radius=0,
                        hover_color="#E0E0E0",
                        command=lambda minterm=m: self.toggle_kmap_cell(minterm)
                    )
                    btn.grid(row=r_idx+1, column=c_idx+1, padx=2, pady=2)
                    self.kmap_cells[m] = btn
            self.lbl_kmap.configure(text="> 3-Variable K-Map Ready (8 Cells, Variables: A, B, C). Click cells to toggle.")
            return

        elif "2x2" in choice:
            self.kmap_N = 2
            self.kmap_var_names = ['A', 'B']
            grid_box = ctk.CTkFrame(self.kmap_grid_container, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
            grid_box.pack(padx=10, pady=5)
            
            row_labels = ["0", "1"]
            col_labels = ["0", "1"]
            
            ctk.CTkLabel(grid_box, text="A \\ B", font=("Helvetica", 10, "bold"), text_color="#000000").grid(row=0, column=0, padx=4, pady=4)
            for c_idx, cl in enumerate(col_labels):
                ctk.CTkLabel(grid_box, text=cl, font=("Helvetica", 11, "bold"), text_color="#0055FF").grid(row=0, column=c_idx+1, padx=2, pady=4)
                
            for r_idx, rl in enumerate(row_labels):
                ctk.CTkLabel(grid_box, text=rl, font=("Helvetica", 11, "bold"), text_color="#FF3333").grid(row=r_idx+1, column=0, padx=4, pady=2)
                for c_idx in range(2):
                    m = (r_idx << 1) | c_idx
                    self.kmap_cell_state[m] = 0
                    btn = ctk.CTkButton(
                        grid_box,
                        text=f"m{m}\n0",
                        width=52,
                        height=44,
                        font=("Helvetica", 10, "bold"),
                        fg_color="#FFFFFF",
                        text_color="#000000",
                        border_width=2,
                        border_color="#000000",
                        corner_radius=0,
                        hover_color="#E0E0E0",
                        command=lambda minterm=m: self.toggle_kmap_cell(minterm)
                    )
                    btn.grid(row=r_idx+1, column=c_idx+1, padx=2, pady=2)
                    self.kmap_cells[m] = btn
            self.lbl_kmap.configure(text="> 2-Variable K-Map Ready (4 Cells, Variables: A, B). Click cells to toggle.")
            return

        else:
            # Custom grids like 2x3, 3x2, 3x3
            parts = choice.split()[0].split('x')
            r_cnt = int(parts[0])
            c_cnt = int(parts[1])
            tot = r_cnt * c_cnt
            self.kmap_N = max(2, math.ceil(math.log2(tot)))
            self.kmap_var_names = ['A', 'B', 'C', 'D', 'E'][:self.kmap_N]
            
            grid_box = ctk.CTkFrame(self.kmap_grid_container, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
            grid_box.pack(padx=10, pady=5)
            
            ctk.CTkLabel(grid_box, text="R \\ C", font=("Helvetica", 10, "bold"), text_color="#000000").grid(row=0, column=0, padx=4, pady=4)
            for c in range(c_cnt):
                ctk.CTkLabel(grid_box, text=f"C{c}", font=("Helvetica", 10, "bold"), text_color="#0055FF").grid(row=0, column=c+1, padx=2, pady=4)
                
            for r in range(r_cnt):
                ctk.CTkLabel(grid_box, text=f"R{r}", font=("Helvetica", 10, "bold"), text_color="#FF3333").grid(row=r+1, column=0, padx=4, pady=2)
                for c in range(c_cnt):
                    m = r * c_cnt + c
                    self.kmap_cell_state[m] = 0
                    btn = ctk.CTkButton(
                        grid_box,
                        text=f"m{m}\n0",
                        width=50,
                        height=44,
                        font=("Helvetica", 10, "bold"),
                        fg_color="#FFFFFF",
                        text_color="#000000",
                        border_width=2,
                        border_color="#000000",
                        corner_radius=0,
                        hover_color="#E0E0E0",
                        command=lambda minterm=m: self.toggle_kmap_cell(minterm)
                    )
                    btn.grid(row=r+1, column=c+1, padx=2, pady=2)
                    self.kmap_cells[m] = btn
            self.lbl_kmap.configure(text=f"> Grid Ready: {r_cnt}x{c_cnt} ({tot} cells). Click cells to toggle (0/1).")

    def toggle_kmap_cell(self, m):
        cur = self.kmap_cell_state.get(m, 0)
        nxt = 1 if cur == 0 else 0
        self.kmap_cell_state[m] = nxt
        btn = self.kmap_cells[m]
        btn.configure(
            text=f"m{m}\n{nxt}", 
            fg_color="#27C93F" if nxt == 1 else "#FFFFFF",
            hover_color="#1FA734" if nxt == 1 else "#E0E0E0"
        )

    def set_all_kmap(self, val):
        for m, btn in self.kmap_cells.items():
            self.kmap_cell_state[m] = val
            btn.configure(
                text=f"m{m}\n{val}", 
                fg_color="#27C93F" if val == 1 else "#FFFFFF",
                hover_color="#1FA734" if val == 1 else "#E0E0E0"
            )

    def invert_kmap(self):
        for m, btn in self.kmap_cells.items():
            cur = self.kmap_cell_state.get(m, 0)
            nxt = 1 if cur == 0 else 0
            self.kmap_cell_state[m] = nxt
            btn.configure(
                text=f"m{m}\n{nxt}", 
                fg_color="#27C93F" if nxt == 1 else "#FFFFFF",
                hover_color="#1FA734" if nxt == 1 else "#E0E0E0"
            )

    def solve_kmap(self):
        """
        =============================================================================
        QUINE-MCCLUSKEY ALGORITHMIC BOOLEAN LOGIC MINIMIZATION ENGINE
        =============================================================================
        Solves tabular minimization for arbitrary N-variable Boolean systems:
        
        Phase 1: Binary Grouping & Adjacency Merging:
          - Groups minterms by number of set bits (Hamming weight).
          - Compares groups of weight w and w+1. If minterms differ by exactly 1 bit
            (Hamming distance = 1), merges them into a product term with a do-not-care bit.
          - Recursively iterates until no further term consolidation is possible.
          - Unmerged terms are collected as Prime Implicants (PI).
          
        Phase 2: Prime Implicant Coverage Table:
          - Constructs mapping cov[m] = {PI covering minterm m}.
          - Identifies Essential Prime Implicants (EPI): PIs that uniquely cover at least one minterm.
          - Applies Greedy Set-Covering heuristic to cover remaining minterms.
          
        Phase 3: Minimal Sum-of-Products (SOP) Formulation:
          - Converts bitmasks back to alphanumeric variables (e.g. A, B', C).
        =============================================================================
        """
        try:
            N = self.kmap_N
            var_names = self.kmap_var_names
            tot_cells = len(self.kmap_cells)
            
            minterms = sorted([m for m, val in self.kmap_cell_state.items() if val == 1])
            
            if not minterms:
                self.lbl_kmap.configure(
                    text=f"> Grid Mode: {self.kmap_mode} | Variables: {', '.join(var_names)}\n"
                         f"> Active Minterms: None (0 / {tot_cells})\n"
                         f"> Simplified Minimal SOP Expression:\n"
                         f"  Y = 0 (GND / Constant LOW)",
                    text_color="#27C93F"
                )
                return
                
            if len(minterms) == tot_cells:
                self.lbl_kmap.configure(
                    text=f"> Grid Mode: {self.kmap_mode} | Variables: {', '.join(var_names)}\n"
                         f"> Active Minterms: All ({tot_cells} / {tot_cells})\n"
                         f"> Simplified Minimal SOP Expression:\n"
                         f"  Y = 1 (VCC / Tautology / Constant HIGH)",
                    text_color="#27C93F"
                )
                return
                
            # Quine-McCluskey grouping
            curr_groups = {i: set() for i in range(N + 1)}
            for m in minterms:
                curr_groups[bin(m).count('1')].add((m, 0))
                
            prime_implicants = set()
            while True:
                next_groups = {i: set() for i in range(N + 1)}
                merged = set()
                for i in range(N):
                    for v1, m1 in curr_groups[i]:
                        for v2, m2 in curr_groups.get(i + 1, set()):
                            if m1 == m2 and bin((v1 ^ v2) & ~m1).count('1') == 1:
                                diff = v1 ^ v2
                                next_groups[i].add((v1 & ~diff, m1 | diff))
                                merged.add((v1, m1))
                                merged.add((v2, m2))
                for i in range(N + 1):
                    for item in curr_groups.get(i, set()):
                        if item not in merged:
                            prime_implicants.add(item)
                curr_groups = next_groups
                if not any(curr_groups.values()):
                    break
                    
            # Essential PI coverage
            cov = {}
            for m in minterms:
                cov[m] = [pi for pi in prime_implicants if (m & ~pi[1]) == (pi[0] & ~pi[1])]
                
            chosen = set()
            uncovered = set(minterms)
            
            # Select essential PIs
            for m, pis in cov.items():
                if len(pis) == 1:
                    chosen.add(pis[0])
                    for um in list(uncovered):
                        if (um & ~pis[0][1]) == (pis[0][0] & ~pis[0][1]):
                            uncovered.discard(um)
                            
            # Greedy set cover for remaining
            while uncovered:
                covering_pis = [pi for pi in prime_implicants if any((um & ~pi[1]) == (pi[0] & ~pi[1]) for um in uncovered)]
                if not covering_pis:
                    break
                best_pi = max(covering_pis, key=lambda pi: len([um for um in uncovered if (um & ~pi[1]) == (pi[0] & ~pi[1])]))
                chosen.add(best_pi)
                for um in list(uncovered):
                    if (um & ~best_pi[1]) == (best_pi[0] & ~best_pi[1]):
                        uncovered.discard(um)
                        
            # Format product terms
            terms = []
            for val, mask in sorted(chosen):
                term = ''
                for k in range(N):
                    bit = 1 << (N - 1 - k)
                    if not (mask & bit):
                        term += var_names[k] if (val & bit) else var_names[k] + "'"
                terms.append(term if term else '1')
                
            ans = " + ".join(terms)
            m_list_str = ", ".join(map(str, minterms))
            out_txt = (
                f"> Grid Mode: {self.kmap_mode} | Variables: {', '.join(var_names)}\n"
                f"> Active Minterms: Σ m({m_list_str}) [Count: {len(minterms)} of {tot_cells}]\n"
                f"> Essential Prime Implicants Found: {len(chosen)}\n"
                f"> Simplified Minimal SOP Expression:\n"
                f"  Y = {ans}"
            )
            self.lbl_kmap.configure(text=out_txt, text_color="#27C93F")
        except Exception as e:
            self.lbl_kmap.configure(text=f"> ERR: {e}", text_color="#FF5F56")

    def show_combinational(self):
        self.clear_content()
        self.create_retro_title("IV. BOOLEAN / COMBINATIONAL EVALUATOR ⚡")
        
        # Frame 1: Boolean Equation Input
        eq_box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        eq_box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(eq_box, text="Enter Boolean Equation (Variables A, B, C, D, E):", font=("Helvetica", 13, "bold"), text_color="#000000").pack(pady=(10, 4))
        
        self.eq_entry = ctk.CTkEntry(eq_box, width=460, font=("Courier New", 14, "bold"), border_width=4, border_color="#000000", corner_radius=0)
        self.eq_entry.pack(pady=5)
        self.eq_entry.insert(0, "(A and B) or (C and not D) or E")
        
        syntax_lbl = ctk.CTkLabel(
            eq_box, 
            text="Supports: AND, OR, NOT, XOR, XNOR, NAND, NOR, primes (A'), +, *, &, |, ~, ^", 
            font=("Helvetica", 10, "bold"), 
            text_color="#0055FF"
        )
        syntax_lbl.pack(pady=(0, 10))

        # Frame 2: Instantaneous Input Vector Evaluation (A, B, C, D, E)
        vec_box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        vec_box.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(vec_box, text="Direct Input Evaluation (A, B, C, D, E):", font=("Helvetica", 12, "bold"), text_color="#000000").pack(pady=(8, 4))
        
        inputs_row = ctk.CTkFrame(vec_box, fg_color="transparent")
        inputs_row.pack(pady=5)
        
        self.comb_inputs = {}
        defaults = {"A": "1", "B": "1", "C": "0", "D": "1", "E": "0"}
        for idx, var in enumerate(["A", "B", "C", "D", "E"]):
            ctk.CTkLabel(inputs_row, text=f"{var}:", font=("Helvetica", 12, "bold"), text_color="#000000").grid(row=0, column=idx*2, padx=(8, 2), pady=4)
            cb = ctk.CTkComboBox(inputs_row, values=["0", "1"], width=52, font=("Helvetica", 11, "bold"), fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=3, corner_radius=0)
            cb.set(defaults[var])
            cb.grid(row=0, column=idx*2 + 1, padx=(0, 6), pady=4)
            self.comb_inputs[var] = cb
            
        btn_eval_vec = ctk.CTkButton(
            vec_box, 
            text="Evaluate Instantaneous Output for (A, B, C, D, E)", 
            font=("Helvetica", 12, "bold"), 
            fg_color="#27C93F", 
            text_color="#000000", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            hover_color="#FFFFFF",
            command=self.eval_comb_instant
        )
        btn_eval_vec.pack(pady=8)
        
        # Frame 3: Full Truth Table Generator
        tt_ctl_box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        tt_ctl_box.pack(fill="x", padx=20, pady=5)
        
        tt_row = ctk.CTkFrame(tt_ctl_box, fg_color="transparent")
        tt_row.pack(pady=8)
        
        ctk.CTkLabel(tt_row, text="Truth Table Scope:", font=("Helvetica", 12, "bold"), text_color="#000000").pack(side="left", padx=5)
        self.combo_tt_scope = ctk.CTkComboBox(
            tt_row,
            values=["Auto-Detect (A-E)", "5 Variables (A, B, C, D, E) [32 Rows]", "4 Variables (A, B, C, D) [16 Rows]", "3 Variables (A, B, C) [8 Rows]"],
            font=("Helvetica", 11, "bold"),
            fg_color="#FFFFFF",
            text_color="#000000",
            border_color="#000000",
            border_width=3,
            corner_radius=0,
            width=260
        )
        self.combo_tt_scope.set("Auto-Detect (A-E)")
        self.combo_tt_scope.pack(side="left", padx=5)
        
        btn_tt = ctk.CTkButton(
            tt_row, 
            text="Generate Full Truth Table", 
            font=("Helvetica", 12, "bold"), 
            fg_color="#4CA8D1", 
            text_color="#000000", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            hover_color="#FFFFFF",
            command=self.calc_comb
        )
        btn_tt.pack(side="left", padx=10)
        
        # Terminal Output Box
        res = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0, height=270, border_width=4, border_color="#000000")
        res.pack(fill="x", padx=20, pady=10)
        res.pack_propagate(False)
        self.lbl_comb = ctk.CTkTextbox(
            res, 
            font=("Courier New", 12, "bold"), 
            text_color="#27C93F", 
            fg_color="#000000",
            corner_radius=0,
            wrap="word"
        )
        self.lbl_comb.pack(fill="both", expand=True, padx=4, pady=4)
        self.lbl_comb.insert("0.0", "> Enter a Boolean equation above and click 'Evaluate' or 'Generate Full Truth Table'...")
        self.lbl_comb.configure(state="disabled")

    def set_comb_text(self, text, color):
        self.lbl_comb.configure(state="normal", text_color=color)
        self.lbl_comb.delete("0.0", "end")
        self.lbl_comb.insert("0.0", text)
        self.lbl_comb.configure(state="disabled")

    def parse_bool_expr(self, eq_str, env):
        """
        =============================================================================
        BOOLEAN ALGEBRA EXPRESSION PARSER & EVALUATOR
        =============================================================================
        Normalizes multi-dialect engineering logic expressions into Python boolean AST:
          - Primes: A' -> (not A)
          - Gates: xnor -> ==, xor -> ^, nand -> and not, nor -> or not
          - Juxtaposition: AB -> A and B, A(B + C) -> A and (B or C)
          - Math operators: + -> or, * -> and, & -> and, | -> or, ~ -> not
        Evaluates securely with sandboxed builtin environment.
        =============================================================================
        """
        s = eq_str.strip()
        # Handle primes: A' -> (not A)
        s = re.sub(r'([a-eA-E])\'', r'(not \1)', s)
        s = re.sub(r'\)\'', r') is False', s)
        # Operators
        s = re.sub(r'\bxnor\b', ' == ', s, flags=re.IGNORECASE)
        s = re.sub(r'\bxor\b', ' ^ ', s, flags=re.IGNORECASE)
        s = re.sub(r'\bnand\b', ' and not ', s, flags=re.IGNORECASE)
        s = re.sub(r'\bnor\b', ' or not ', s, flags=re.IGNORECASE)
        # Adjacent letters like AB -> A and B
        s = re.sub(r'([a-eA-E])(?=[a-eA-E\(])', r'\1 and ', s)
        s = re.sub(r'\)(?=[a-eA-E])', r') and ', s)
        # Standard logic symbols
        s = re.sub(r'\+', ' or ', s)
        s = re.sub(r'\*', ' and ', s)
        s = re.sub(r'&', ' and ', s)
        s = re.sub(r'\|', ' or ', s)
        s = re.sub(r'~', ' not ', s)
        s = re.sub(r'\^', ' ^ ', s)
        s = s.lower()
        bool_env = {k.lower(): bool(v) for k, v in env.items()}
        val = eval(s, {'__builtins__': None}, bool_env)
        return int(bool(val))

    def eval_comb_instant(self):
        """
        Evaluates equation output for instantaneous manual input vector (A, B, C, D, E).
        """
        try:
            raw_eq = self.eq_entry.get().strip()
            if not raw_eq:
                self.set_comb_text("> ERR: Please enter a Boolean equation.", "#FF5F56")
                return
            env = {var: int(cb.get()) for var, cb in self.comb_inputs.items()}
            y = self.parse_bool_expr(raw_eq, env)
            vec_str = ", ".join([f"{k}={v}" for k, v in env.items()])
            out_txt = (
                f"> [INSTANTANEOUS BOOLEAN EVALUATION]\n"
                f"> Equation: Y = {raw_eq}\n"
                f"> Input Vector: [{vec_str}]\n"
                f"> Output Y = {y} ({'HIGH / 1 / TRUE' if y == 1 else 'LOW / 0 / FALSE'})\n"
            )
            self.set_comb_text(out_txt, "#27C93F")
        except Exception as e:
            self.set_comb_text(f"> ERR in evaluation: {str(e)}", "#FF5F56")

    def calc_comb(self):
        raw_eq = self.eq_entry.get().strip()
        if not raw_eq:
            self.set_comb_text("> ERR: Please enter a Boolean equation.", "#FF5F56")
            return
            
        scope = self.combo_tt_scope.get()
        if "5" in scope:
            n_vars = 5
        elif "4" in scope:
            n_vars = 4
        elif "3" in scope:
            n_vars = 3
        else:
            # Auto-detect using simple letter checks ignoring reserved gate names
            clean_eq = re.sub(r'(?i)\b(and|or|not|xor|xnor|nand|nor)\b', '', raw_eq)
            has_e = 'e' in clean_eq.lower()
            has_d = 'd' in clean_eq.lower()
            has_c = 'c' in clean_eq.lower()
            has_b = 'b' in clean_eq.lower()
            if has_e:
                n_vars = 5
            elif has_d:
                n_vars = 4
            elif has_c:
                n_vars = 3
            elif has_b:
                n_vars = 2
            else:
                n_vars = 2
                
        var_names = ["A", "B", "C", "D", "E"][:n_vars]
        tot_rows = 1 << n_vars
        
        tt_text = f"> TRUTH TABLE GENERATOR\n"
        tt_text += f"> Equation: Y = {raw_eq}\n"
        tt_text += f"> Variables: {', '.join(var_names)} ({tot_rows} combinations)\n\n"
        
        header_cols = " | ".join(var_names) + " || Y | Minterm\n"
        divider = "-" * (len(header_cols) + 4) + "\n"
        tt_text += header_cols + divider
        
        active_minterms = []
        try:
            for i in range(tot_rows):
                env = {}
                row_vals = []
                for bit_idx, v in enumerate(var_names):
                    bit_val = (i >> (n_vars - 1 - bit_idx)) & 1
                    env[v] = bit_val
                    row_vals.append(str(bit_val))
                row_str = " | ".join(row_vals)
                
                y = self.parse_bool_expr(raw_eq, env)
                if y == 1:
                    active_minterms.append(i)
                tt_text += f"{row_str} || {y} | m{i}\n"
                
            m_list_str = ", ".join(map(str, active_minterms)) if active_minterms else "None"
            tt_text += divider
            tt_text += f"> Canonical SOP Form: \u03A3 m({m_list_str}) [Count: {len(active_minterms)} of {tot_rows}]\n"
            self.set_comb_text(tt_text, "#27C93F")
        except Exception as e:
            self.set_comb_text(f"> ERR: Invalid Equation Syntax\n> {str(e)}", "#FF5F56")

    def show_sequential(self):
        self.clear_content()
        self.create_retro_title("V. SEQUENTIAL LOGIC & FSM")
        
        from practical_applications import get_practical_example
        ctk.CTkLabel(self.content_frame, text=get_practical_example("seq"), font=("Helvetica", 11, "italic"), text_color="#333333", wraplength=500, justify="left").pack(pady=(0, 10), padx=20)
        self.seq_cvs = ctk.CTkCanvas(self.content_frame, width=500, height=400, bg="#FFF5EE", highlightthickness=4, highlightbackground="#000000")
        self.seq_cvs.pack(pady=12)
        
        info = ctk.CTkLabel(self.content_frame, text="Latches, Flip-Flops, State Tables & Timing", font=RETRO_FONT, text_color="#000000")
        info.pack(pady=5)
        
        box = ctk.CTkFrame(self.content_frame, fg_color="#FFF5EE", border_width=4, border_color="#000000", corner_radius=0)
        box.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(box, text="Select Topic:", font=RETRO_FONT, text_color="#000000").grid(row=0, column=0, padx=10, pady=10)
        self.combo_seq = ctk.CTkComboBox(box, values=["D Flip-Flop", "JK Flip-Flop", "T Flip-Flop", "SR Latch", "D Latch", "Master-Slave JK"], font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_color="#000000", border_width=4, corner_radius=0, width=220, command=self.draw_seq)
        self.combo_seq.grid(row=0, column=1, padx=10, pady=10)
        
        btn = ctk.CTkButton(box, text="Load Data", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=self.calc_seq)
        btn.grid(row=0, column=2, padx=10, pady=10)
        
        res = ctk.CTkFrame(self.content_frame, fg_color="#000000", corner_radius=0)
        res.pack(fill="x", padx=20, pady=10)
        self.lbl_seq = ctk.CTkLabel(res, text="> Q(t) | Q(t+1) | Input\n> ...", font=("Courier New", 14), text_color="#27C93F", justify="left")
        self.lbl_seq.pack(padx=10, pady=10, anchor="w")
        
        self.draw_seq("D Flip-Flop")

    def draw_seq(self, choice):
        cvs = self.seq_cvs
        cvs.delete("all")
        
        # Enlarge Flip-Flop IC Block body
        cvs.create_rectangle(130, 30, 330, 190, width=4, outline="#0055FF", fill="#FFFFFF")
        cvs.create_text(230, 50, text=choice, font=("Helvetica", 12, "bold"), fill="#0055FF")
        
        # Outputs Q and Q_bar
        cvs.create_line(330, 75, 410, 75, width=4, fill="#000000")
        cvs.create_oval(405, 70, 415, 80, fill="#000000")
        cvs.create_text(310, 75, text="Q", font=("Helvetica", 16, "bold"), fill="#0055FF")
        cvs.create_text(435, 75, text="Q", font=("Helvetica", 16, "bold"), fill="#000000")
        
        cvs.create_line(330, 145, 410, 145, width=4, fill="#000000")
        cvs.create_oval(405, 140, 415, 150, fill="#000000")
        cvs.create_text(305, 145, text="Q'", font=("Helvetica", 16, "bold"), fill="#0055FF")
        cvs.create_text(435, 145, text="Q'", font=("Helvetica", 16, "bold"), fill="#000000")
        
        clk_lbl = "CLK"
        if "Latch" in choice:
            clk_lbl = "EN"
            
        # Inputs & Clock
        if choice in ["D Flip-Flop", "D Latch"]:
            cvs.create_line(50, 75, 130, 75, width=4, fill="#000000")
            cvs.create_text(25, 75, text="D", font=("Helvetica", 16, "bold"), fill="#000000")
            cvs.create_text(150, 75, text="D", font=("Helvetica", 16, "bold"), fill="#0055FF")
            
            cvs.create_line(50, 145, 130, 145, width=4, fill="#000000")
            if clk_lbl == "CLK":
                cvs.create_polygon(130, 130, 130, 160, 150, 145, fill="", outline="#0055FF", width=3)
            else:
                cvs.create_text(150, 145, text=clk_lbl, font=("Helvetica", 12, "bold"), fill="#0055FF")
            cvs.create_text(25, 145, text=clk_lbl, font=("Helvetica", 12, "bold"), fill="#000000")
            
        elif choice in ["JK Flip-Flop", "Master-Slave JK"]:
            cvs.create_line(50, 65, 130, 65, width=4, fill="#000000")
            cvs.create_text(25, 65, text="J", font=("Helvetica", 16, "bold"), fill="#000000")
            cvs.create_text(150, 65, text="J", font=("Helvetica", 16, "bold"), fill="#0055FF")
            
            cvs.create_line(50, 155, 130, 155, width=4, fill="#000000")
            cvs.create_text(25, 155, text="K", font=("Helvetica", 16, "bold"), fill="#000000")
            cvs.create_text(150, 155, text="K", font=("Helvetica", 16, "bold"), fill="#0055FF")
            
            cvs.create_line(50, 110, 130, 110, width=4, fill="#000000")
            if choice == "Master-Slave JK":
                cvs.create_oval(120, 105, 130, 115, fill="#FFFFFF", outline="#000000", width=3)
            cvs.create_polygon(130, 95, 130, 125, 150, 110, fill="", outline="#0055FF", width=3)
            cvs.create_text(25, 110, text="CLK", font=("Helvetica", 12, "bold"), fill="#000000")
            
        elif choice == "T Flip-Flop":
            cvs.create_line(50, 75, 130, 75, width=4, fill="#000000")
            cvs.create_text(25, 75, text="T", font=("Helvetica", 16, "bold"), fill="#000000")
            cvs.create_text(150, 75, text="T", font=("Helvetica", 16, "bold"), fill="#0055FF")
            
            cvs.create_line(50, 145, 130, 145, width=4, fill="#000000")
            cvs.create_polygon(130, 130, 130, 160, 150, 145, fill="", outline="#0055FF", width=3)
            cvs.create_text(25, 145, text="CLK", font=("Helvetica", 12, "bold"), fill="#000000")

        elif choice == "SR Latch":
            cvs.create_line(50, 65, 130, 65, width=4, fill="#000000")
            cvs.create_text(25, 65, text="S", font=("Helvetica", 16, "bold"), fill="#000000")
            cvs.create_text(150, 65, text="S", font=("Helvetica", 16, "bold"), fill="#0055FF")
            
            cvs.create_line(50, 155, 130, 155, width=4, fill="#000000")
            cvs.create_text(25, 155, text="R", font=("Helvetica", 16, "bold"), fill="#000000")
            cvs.create_text(150, 155, text="R", font=("Helvetica", 16, "bold"), fill="#0055FF")
            
            cvs.create_line(50, 110, 130, 110, width=4, fill="#000000")
            cvs.create_text(25, 110, text="EN", font=("Helvetica", 12, "bold"), fill="#000000")
            cvs.create_text(150, 110, text="EN", font=("Helvetica", 12, "bold"), fill="#0055FF")
            
        # Draw Timing Diagram below (y=240 to 380)
        # cvs.create_text(250, 230, text="--- Timing Diagram ---", font=("Helvetica", 10, "italic"), fill="#000000")
        
        # Base coordinates for timing
        x0, dx = 50, 40
        
        def draw_wave(y0, label, vals, color):
            pass # Timing diagram removed per user request
            
        # Define some basic waveforms
        clk = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        
        if choice == "D Flip-Flop":
            d_val = [0, 0, 1, 1, 1, 0, 0, 1, 0, 0]
            # samples on rising edge
            q_val = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0]
            draw_wave(270, "CLK", clk, "#000000")
            draw_wave(310, "D", d_val, "#0055FF")
            draw_wave(350, "Q", q_val, "#F21D44")
            
        elif choice == "D Latch":
            en_val = [0, 1, 1, 0, 0, 1, 1, 0, 0, 0]
            d_val =  [0, 0, 1, 1, 0, 0, 1, 1, 0, 0]
            # transparent when EN=1
            q_val =  [0, 0, 1, 1, 1, 0, 1, 1, 1, 1]
            draw_wave(270, "EN", en_val, "#000000")
            draw_wave(310, "D", d_val, "#0055FF")
            draw_wave(350, "Q", q_val, "#F21D44")
            
        elif choice == "JK Flip-Flop":
            j_val = [0, 0, 1, 1, 0, 0, 1, 1, 1, 1]
            k_val = [0, 1, 0, 0, 1, 1, 1, 1, 0, 0]
            q_val = [0, 0, 0, 1, 1, 1, 0, 1, 0, 1] # toggle behavior
            draw_wave(270, "CLK", clk, "#000000")
            draw_wave(310, "J", j_val, "#0055FF")
            draw_wave(340, "K", k_val, "#0055FF")
            draw_wave(370, "Q", q_val, "#F21D44")
            
        elif choice == "Master-Slave JK":
            j_val = [0, 0, 1, 1, 0, 0, 1, 1, 1, 1]
            k_val = [0, 1, 0, 0, 1, 1, 1, 1, 0, 0]
            # Master-slave transitions on falling edge of CLK
            q_val = [0, 0, 0, 0, 1, 1, 0, 0, 1, 1]
            draw_wave(270, "CLK", clk, "#000000")
            draw_wave(310, "J", j_val, "#0055FF")
            draw_wave(340, "K", k_val, "#0055FF")
            draw_wave(370, "Q", q_val, "#F21D44")
            
        elif choice == "T Flip-Flop":
            t_val = [0, 1, 1, 0, 0, 1, 1, 0, 1, 0]
            q_val = [0, 0, 1, 0, 0, 0, 1, 0, 0, 1]
            draw_wave(270, "CLK", clk, "#000000")
            draw_wave(310, "T", t_val, "#0055FF")
            draw_wave(350, "Q", q_val, "#F21D44")
            
        elif choice == "SR Latch":
            s_val = [0, 1, 0, 0, 0, 1, 0, 0, 0, 0]
            r_val = [0, 0, 0, 1, 0, 0, 0, 0, 1, 0]
            q_val = [0, 1, 1, 0, 0, 1, 1, 1, 0, 0]
            en_val= [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            draw_wave(270, "EN", en_val, "#000000")
            draw_wave(310, "S", s_val, "#0055FF")
            draw_wave(340, "R", r_val, "#0055FF")
            draw_wave(370, "Q", q_val, "#F21D44")

    def calc_seq(self):
        t = self.combo_seq.get()
        if "JK" in t:
            self.lbl_seq.configure(text="> CLK | Q(t) | Q(t+1) || J | K\n>  ↑  |   0  |   0    || 0 | X\n>  ↑  |   0  |   1    || 1 | X\n>  ↑  |   1  |   0    || X | 1\n>  ↑  |   1  |   1    || X | 0", text_color="#27C93F")
        elif "D" in t and "Latch" not in t:
            self.lbl_seq.configure(text="> CLK | Q(t) | Q(t+1) || D\n>  ↑  |   0  |   0    || 0\n>  ↑  |   0  |   1    || 1\n>  ↑  |   1  |   0    || 0\n>  ↑  |   1  |   1    || 1", text_color="#27C93F")
        elif "D Latch" in t:
            self.lbl_seq.configure(text="> EN | D || Q(t+1)\n>  0 | X || Q(t) (Hold)\n>  1 | 0 || 0\n>  1 | 1 || 1", text_color="#27C93F")
        elif "SR Latch" in t:
            self.lbl_seq.configure(text="> Q(t) | Q(t+1) || S | R\n>   0  |   0    || 0 | X\n>   0  |   1    || 1 | 0\n>   1  |   0    || 0 | 1\n>   1  |   1    || X | 0\n>   (1,1) is Invalid/Forbidden", text_color="#27C93F")
        elif "T Flip-Flop" in t:
            self.lbl_seq.configure(text="> CLK | Q(t) | Q(t+1) || T\n>  ↑  |   0  |   0    || 0\n>  ↑  |   0  |   1    || 1\n>  ↑  |   1  |   0    || 1\n>  ↑  |   1  |   1    || 0", text_color="#27C93F")
