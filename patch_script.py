import re

with open("dc_ac_circuits_engine.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remove Custom Netlist Tab
code = re.sub(r'self\.btn_custom = self\.create_nav_btn\("🛠 Custom Netlist Solver", self\.show_custom_circuit, 7\)\n?', '', code)

# Remove the custom netlist methods at the end
code = re.sub(r'    def show_custom_circuit\(self\):.*', '', code, flags=re.DOTALL)

# 2. Add drawing helper methods before update_diode_app
helpers = """
    def draw_res_h(self, cvs, x1, y1, x2, y2):
        pts = [x1, y1, x1+10, y1, x1+13, y1-8, x1+19, y1+8, x1+25, y1-8, x1+31, y1+8, x1+37, y1-8, x1+40, y1, x2, y2]
        cvs.create_line(*pts, width=2)

    def draw_res_v(self, cvs, x1, y1, x2, y2):
        pts = [x1, y1, x1, y1+10, x1-8, y1+13, x1+8, y1+19, x1-8, y1+25, x1+8, y1+31, x1-8, y1+37, x1, y1+40, x2, y2]
        cvs.create_line(*pts, width=2)

    def draw_diode_sym(self, cvs, x, y):
        cvs.create_polygon(x-10, y-10, x-10, y+10, x+10, y, fill="black", outline="black", width=2)
        cvs.create_line(x+10, y-15, x+10, y+15, width=2, fill="black")

    def draw_bjt_npn(self, cvs, x, y):
        cvs.create_line(x, y, x+10, y, width=2) # base lead
        cvs.create_line(x+10, y-15, x+10, y+15, width=3) # base plate
        cvs.create_line(x+10, y-10, x+25, y-25, width=2) # collector
        cvs.create_line(x+25, y-25, x+25, y-40, width=2)
        cvs.create_line(x+10, y+10, x+25, y+25, width=2) # emitter
        cvs.create_polygon(x+20, y+25, x+25, y+25, x+25, y+20, fill="black") # arrow
        cvs.create_line(x+25, y+25, x+25, y+40, width=2)

    def draw_jfet_n(self, cvs, x, y):
        cvs.create_line(x, y, x+15, y, width=2) # gate lead
        cvs.create_polygon(x+8, y-4, x+15, y, x+8, y+4, fill="black") # arrow
        cvs.create_line(x+15, y-15, x+15, y+15, width=3) # channel
        cvs.create_line(x+15, y-12, x+30, y-12, width=2) # drain
        cvs.create_line(x+30, y-12, x+30, y-30, width=2)
        cvs.create_line(x+15, y+12, x+30, y+12, width=2) # source
        cvs.create_line(x+30, y+12, x+30, y+30, width=2)

    def draw_dmos_n(self, cvs, x, y):
        cvs.create_line(x, y, x+10, y, width=2)
        cvs.create_line(x+10, y-15, x+10, y+15, width=2) # gate plate
        cvs.create_line(x+14, y-15, x+14, y+15, width=3) # channel
        cvs.create_line(x+14, y-12, x+30, y-12, width=2) # drain
        cvs.create_line(x+30, y-12, x+30, y-30, width=2)
        cvs.create_line(x+14, y+12, x+30, y+12, width=2) # source
        cvs.create_line(x+30, y+12, x+30, y+30, width=2)
        
    def draw_emos_n(self, cvs, x, y):
        cvs.create_line(x, y, x+10, y, width=2)
        cvs.create_line(x+10, y-15, x+10, y+15, width=2) # gate
        cvs.create_line(x+14, y-15, x+14, y-5, width=3) # channel pieces
        cvs.create_line(x+14, y-4, x+14, y+4, width=3)
        cvs.create_line(x+14, y+5, x+14, y+15, width=3)
        cvs.create_line(x+14, y-12, x+30, y-12, width=2) # drain
        cvs.create_line(x+30, y-12, x+30, y-30, width=2)
        cvs.create_line(x+14, y+12, x+30, y+12, width=2) # source
        cvs.create_line(x+30, y+12, x+30, y+30, width=2)

    def update_diode_app(self, choice):
"""

code = code.replace("    def update_diode_app(self, choice):", helpers)

# Diode replacements
diode_orig = '''        if choice == "Half-wave":
            self.diode_canvas.create_line(50, 100, 150, 100, width=2)
            self.diode_canvas.create_polygon(150, 90, 150, 110, 170, 100, fill="black")
            self.diode_canvas.create_line(170, 90, 170, 110, width=2)
            self.diode_canvas.create_line(170, 100, 250, 100, width=2)
            self.diode_canvas.create_rectangle(250, 80, 290, 120, width=2)
            self.create_diode_input("Peak Input AC Volts (Vm):", "170")
            btn = ctk.CTkButton(self.diode_form, text="Calculate Half-wave", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("Half-wave"))
            btn.grid(row=1, column=0, columnspan=2, pady=10)
        elif choice == "Full-wave":
            self.diode_canvas.create_rectangle(150, 50, 250, 150, width=2)
            self.diode_canvas.create_line(50, 100, 150, 100, width=2)
            self.diode_canvas.create_line(250, 100, 350, 100, width=2)
            self.create_diode_input("Peak Input AC Volts (Vm):", "170")
            btn = ctk.CTkButton(self.diode_form, text="Calculate Full-wave", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("Full-wave"))
            btn.grid(row=1, column=0, columnspan=2, pady=10)
        elif choice == "Clipper":
            self.diode_canvas.create_line(50, 50, 150, 50, width=2)
            self.diode_canvas.create_rectangle(150, 40, 190, 60, width=2)
            self.diode_canvas.create_line(190, 50, 300, 50, width=2)
            self.diode_canvas.create_line(250, 50, 250, 100, width=2)
            self.diode_canvas.create_polygon(240, 100, 260, 100, 250, 120, fill="black")
            self.diode_canvas.create_line(240, 120, 260, 120, width=2)
            self.diode_canvas.create_line(250, 120, 250, 150, width=2)
            self.create_diode_input("Input Peak (Vi):", "10")
            btn = ctk.CTkButton(self.diode_form, text="Calculate Clipper", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("Clipper"))
            btn.grid(row=1, column=0, columnspan=2, pady=10)
        elif choice == "Clamper":
            self.diode_canvas.create_line(50, 50, 150, 50, width=2)
            self.diode_canvas.create_line(150, 30, 150, 70, width=2)
            self.diode_canvas.create_line(170, 30, 170, 70, width=2)
            self.diode_canvas.create_line(170, 50, 300, 50, width=2)
            self.diode_canvas.create_line(250, 50, 250, 100, width=2)
            self.diode_canvas.create_polygon(240, 100, 260, 100, 250, 120, fill="black")
            self.diode_canvas.create_line(240, 120, 260, 120, width=2)
            self.diode_canvas.create_line(250, 120, 250, 150, width=2)
            self.create_diode_input("Input Peak (Vi):", "10")
            btn = ctk.CTkButton(self.diode_form, text="Calculate Clamper", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("Clamper"))
            btn.grid(row=1, column=0, columnspan=2, pady=10)
        elif choice == "LED":
            self.diode_canvas.create_line(50, 100, 100, 100, width=2)
            self.diode_canvas.create_rectangle(100, 90, 140, 110, width=2)
            self.diode_canvas.create_line(140, 100, 200, 100, width=2)
            self.diode_canvas.create_polygon(200, 90, 200, 110, 220, 100, fill="black")
            self.diode_canvas.create_line(220, 90, 220, 110, width=2)
            self.diode_canvas.create_line(220, 100, 280, 100, width=2)
            self.create_diode_input("Vcc (V):", "5", 0)
            self.create_diode_input("Vf (LED Drop):", "2", 1)
            self.create_diode_input("Id (Desired mA):", "15", 2)
            btn = ctk.CTkButton(self.diode_form, text="Calculate Resistor", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("LED"))
            btn.grid(row=3, column=0, columnspan=2, pady=10)'''

diode_new = '''        if choice == "Half-wave":
            self.diode_canvas.create_line(50, 100, 140, 100, width=2)
            self.draw_diode_sym(self.diode_canvas, 150, 100)
            self.diode_canvas.create_line(160, 100, 240, 100, width=2)
            self.draw_res_v(self.diode_canvas, 240, 80, 240, 120)
            self.create_diode_input("Peak Input AC Volts (Vm):", "170")
            btn = ctk.CTkButton(self.diode_form, text="Calculate Half-wave", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("Half-wave"))
            btn.grid(row=1, column=0, columnspan=2, pady=10)
        elif choice == "Full-wave":
            self.diode_canvas.create_line(50, 100, 150, 100, width=2)
            self.draw_diode_sym(self.diode_canvas, 200, 50)
            self.draw_diode_sym(self.diode_canvas, 200, 150)
            self.diode_canvas.create_line(150, 50, 150, 150, width=2)
            self.diode_canvas.create_line(250, 50, 250, 150, width=2)
            self.diode_canvas.create_line(250, 100, 350, 100, width=2)
            self.create_diode_input("Peak Input AC Volts (Vm):", "170")
            btn = ctk.CTkButton(self.diode_form, text="Calculate Full-wave", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("Full-wave"))
            btn.grid(row=1, column=0, columnspan=2, pady=10)
        elif choice == "Clipper":
            self.diode_canvas.create_line(50, 50, 100, 50, width=2)
            self.draw_res_h(self.diode_canvas, 100, 50, 180, 50)
            self.diode_canvas.create_line(180, 50, 300, 50, width=2)
            self.diode_canvas.create_line(250, 50, 250, 90, width=2)
            self.draw_diode_sym(self.diode_canvas, 250, 100)
            self.diode_canvas.create_line(250, 110, 250, 150, width=2)
            self.create_diode_input("Input Peak (Vi):", "10")
            btn = ctk.CTkButton(self.diode_form, text="Calculate Clipper", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("Clipper"))
            btn.grid(row=1, column=0, columnspan=2, pady=10)
        elif choice == "Clamper":
            self.diode_canvas.create_line(50, 50, 130, 50, width=2)
            self.diode_canvas.create_line(130, 30, 130, 70, width=2) # Cap
            self.diode_canvas.create_line(150, 30, 150, 70, width=2) # Cap
            self.diode_canvas.create_line(150, 50, 300, 50, width=2)
            self.diode_canvas.create_line(250, 50, 250, 90, width=2)
            self.draw_diode_sym(self.diode_canvas, 250, 100)
            self.diode_canvas.create_line(250, 110, 250, 150, width=2)
            self.create_diode_input("Input Peak (Vi):", "10")
            btn = ctk.CTkButton(self.diode_form, text="Calculate Clamper", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("Clamper"))
            btn.grid(row=1, column=0, columnspan=2, pady=10)
        elif choice == "LED":
            self.diode_canvas.create_line(50, 100, 80, 100, width=2)
            self.draw_res_h(self.diode_canvas, 80, 100, 150, 100)
            self.diode_canvas.create_line(150, 100, 180, 100, width=2)
            self.draw_diode_sym(self.diode_canvas, 190, 100)
            self.diode_canvas.create_line(200, 100, 280, 100, width=2)
            self.create_diode_input("Vcc (V):", "5", 0)
            self.create_diode_input("Vf (LED Drop):", "2", 1)
            self.create_diode_input("Id (Desired mA):", "15", 2)
            btn = ctk.CTkButton(self.diode_form, text="Calculate Resistor", font=RETRO_FONT, fg_color="#F4A261", text_color="#000000", border_width=4, border_color="#000000", corner_radius=0, command=lambda: self.calc_diode("LED"))
            btn.grid(row=3, column=0, columnspan=2, pady=10)'''

code = code.replace(diode_orig, diode_new)

bjt_orig = '''        if choice == "Fixed Bias":
            self.bias_cvs.create_line(150, 20, 150, 50, width=2)
            self.bias_cvs.create_rectangle(140, 50, 160, 90, width=2)
            self.bias_cvs.create_line(150, 90, 150, 120, width=2)
            self.bias_cvs.create_line(100, 120, 150, 120, width=2)
            self.bias_cvs.create_line(100, 120, 100, 80, width=2)
            self.bias_cvs.create_rectangle(90, 40, 110, 80, width=2)
            self.bias_cvs.create_line(100, 40, 100, 20, width=2)
            self.bias_cvs.create_line(100, 20, 150, 20, width=2)
            self.bias_cvs.create_line(150, 120, 150, 160, width=2)
            self.bias_cvs.create_polygon(140, 130, 160, 130, 150, 140, fill="black")
            inputs = [("Vcc (V):", "12"), ("Rb (kΩ):", "240"), ("Rc (kΩ):", "2.2"), ("Beta:", "50")]
        elif choice == "Voltage Divider":
            self.bias_cvs.create_line(150, 20, 150, 50, width=2)
            self.bias_cvs.create_rectangle(140, 50, 160, 90, width=2)
            self.bias_cvs.create_line(150, 90, 150, 120, width=2)
            self.bias_cvs.create_line(100, 120, 150, 120, width=2)
            self.bias_cvs.create_line(100, 120, 100, 80, width=2)
            self.bias_cvs.create_rectangle(90, 40, 110, 80, width=2)
            self.bias_cvs.create_line(100, 40, 100, 20, width=2)
            self.bias_cvs.create_line(100, 20, 150, 20, width=2)
            self.bias_cvs.create_rectangle(90, 120, 110, 160, width=2)
            self.bias_cvs.create_line(100, 160, 100, 180, width=2)
            self.bias_cvs.create_line(150, 120, 150, 140, width=2)
            self.bias_cvs.create_polygon(140, 130, 160, 130, 150, 140, fill="black")
            self.bias_cvs.create_rectangle(140, 140, 160, 180, width=2)
            inputs = [("Vcc (V):", "22"), ("R1 (kΩ):", "39"), ("R2 (kΩ):", "3.9"), ("Rc (kΩ):", "10"), ("Re (kΩ):", "1.5"), ("Beta:", "140")]
        elif choice == "Emitter Bias":
            self.bias_cvs.create_line(150, 20, 150, 50, width=2)
            self.bias_cvs.create_rectangle(140, 50, 160, 90, width=2)
            self.bias_cvs.create_line(150, 90, 150, 120, width=2)
            self.bias_cvs.create_line(100, 120, 150, 120, width=2)
            self.bias_cvs.create_line(100, 120, 100, 80, width=2)
            self.bias_cvs.create_rectangle(90, 40, 110, 80, width=2)
            self.bias_cvs.create_line(100, 40, 100, 20, width=2)
            self.bias_cvs.create_line(150, 120, 150, 140, width=2)
            self.bias_cvs.create_polygon(140, 130, 160, 130, 150, 140, fill="black")
            self.bias_cvs.create_rectangle(140, 140, 160, 180, width=2)
            inputs = [("Vcc (V):", "20"), ("Rb (kΩ):", "430"), ("Rc (kΩ):", "2"), ("Re (kΩ):", "1"), ("Beta:", "50")]
        elif choice == "Collector Feedback":
            self.bias_cvs.create_line(150, 20, 150, 50, width=2)
            self.bias_cvs.create_rectangle(140, 50, 160, 90, width=2)
            self.bias_cvs.create_line(150, 90, 150, 120, width=2)
            self.bias_cvs.create_line(100, 120, 150, 120, width=2)
            self.bias_cvs.create_line(100, 120, 100, 80, width=2)
            self.bias_cvs.create_rectangle(90, 40, 110, 80, width=2)
            self.bias_cvs.create_line(100, 40, 150, 40, width=2)
            self.bias_cvs.create_line(150, 120, 150, 160, width=2)
            self.bias_cvs.create_polygon(140, 130, 160, 130, 150, 140, fill="black")
            inputs = [("Vcc (V):", "10"), ("Rb (kΩ):", "250"), ("Rc (kΩ):", "4.7"), ("Beta:", "90")]'''

bjt_new = '''        if choice == "Fixed Bias":
            self.draw_bjt_npn(self.bias_cvs, 140, 120)
            self.bias_cvs.create_line(165, 20, 165, 50, width=2)
            self.draw_res_v(self.bias_cvs, 165, 50, 165, 80)
            self.bias_cvs.create_line(165, 80, 165, 95, width=2)
            self.bias_cvs.create_line(140, 120, 100, 120, width=2)
            self.bias_cvs.create_line(100, 120, 100, 80, width=2)
            self.draw_res_v(self.bias_cvs, 100, 50, 100, 80)
            self.bias_cvs.create_line(100, 50, 100, 20, width=2)
            self.bias_cvs.create_line(100, 20, 165, 20, width=2)
            inputs = [("Vcc (V):", "12"), ("Rb (kΩ):", "240"), ("Rc (kΩ):", "2.2"), ("Beta:", "50")]
        elif choice == "Voltage Divider":
            self.draw_bjt_npn(self.bias_cvs, 140, 120)
            self.bias_cvs.create_line(165, 20, 165, 50, width=2)
            self.draw_res_v(self.bias_cvs, 165, 50, 165, 80)
            self.bias_cvs.create_line(165, 80, 165, 95, width=2)
            self.bias_cvs.create_line(140, 120, 100, 120, width=2)
            self.bias_cvs.create_line(100, 120, 100, 80, width=2)
            self.draw_res_v(self.bias_cvs, 100, 50, 100, 80)
            self.bias_cvs.create_line(100, 50, 100, 20, width=2)
            self.bias_cvs.create_line(100, 20, 165, 20, width=2)
            self.bias_cvs.create_line(100, 120, 100, 130, width=2)
            self.draw_res_v(self.bias_cvs, 100, 130, 100, 170)
            self.bias_cvs.create_line(100, 170, 100, 180, width=2)
            self.bias_cvs.create_line(165, 160, 165, 165, width=2)
            self.draw_res_v(self.bias_cvs, 165, 165, 165, 195)
            inputs = [("Vcc (V):", "22"), ("R1 (kΩ):", "39"), ("R2 (kΩ):", "3.9"), ("Rc (kΩ):", "10"), ("Re (kΩ):", "1.5"), ("Beta:", "140")]
        elif choice == "Emitter Bias":
            self.draw_bjt_npn(self.bias_cvs, 140, 120)
            self.bias_cvs.create_line(165, 20, 165, 50, width=2)
            self.draw_res_v(self.bias_cvs, 165, 50, 165, 80)
            self.bias_cvs.create_line(165, 80, 165, 95, width=2)
            self.bias_cvs.create_line(140, 120, 100, 120, width=2)
            self.bias_cvs.create_line(100, 120, 100, 80, width=2)
            self.draw_res_v(self.bias_cvs, 100, 50, 100, 80)
            self.bias_cvs.create_line(100, 50, 100, 20, width=2)
            self.bias_cvs.create_line(165, 160, 165, 170, width=2)
            self.draw_res_v(self.bias_cvs, 165, 170, 165, 200)
            inputs = [("Vcc (V):", "20"), ("Rb (kΩ):", "430"), ("Rc (kΩ):", "2"), ("Re (kΩ):", "1"), ("Beta:", "50")]
        elif choice == "Collector Feedback":
            self.draw_bjt_npn(self.bias_cvs, 140, 120)
            self.bias_cvs.create_line(165, 20, 165, 50, width=2)
            self.draw_res_v(self.bias_cvs, 165, 50, 165, 80)
            self.bias_cvs.create_line(165, 80, 165, 95, width=2)
            self.bias_cvs.create_line(140, 120, 100, 120, width=2)
            self.bias_cvs.create_line(100, 120, 100, 80, width=2)
            self.draw_res_v(self.bias_cvs, 100, 50, 100, 80)
            self.bias_cvs.create_line(100, 50, 165, 50, width=2)
            inputs = [("Vcc (V):", "10"), ("Rb (kΩ):", "250"), ("Rc (kΩ):", "4.7"), ("Beta:", "90")]'''

code = code.replace(bjt_orig, bjt_new)

fet_orig = '''        if choice == "JFET" or choice == "D-MOSFET":
            self.fet_cvs.create_line(150, 20, 150, 50, width=2)
            self.fet_cvs.create_line(130, 50, 170, 50, width=2)
            self.fet_cvs.create_line(150, 50, 150, 100, width=2)
            self.fet_cvs.create_line(130, 100, 170, 100, width=2)
            self.fet_cvs.create_line(150, 100, 150, 130, width=2)
            inputs = [("Idss (mA):", "10"), ("Vp (V):", "-4"), ("Vgs (V):", "-2")]
            btn_txt = "Calculate Id & gm"
        elif choice == "E-MOSFET":
            self.fet_cvs.create_line(150, 20, 150, 50, width=2)
            self.fet_cvs.create_line(130, 50, 170, 50, width=2)
            self.fet_cvs.create_line(150, 50, 150, 70, width=2)
            self.fet_cvs.create_line(130, 70, 170, 70, width=2)
            self.fet_cvs.create_line(150, 70, 150, 90, width=2)
            self.fet_cvs.create_line(130, 90, 170, 90, width=2)
            self.fet_cvs.create_line(150, 90, 150, 130, width=2)
            inputs = [("k (mA/V^2):", "0.3"), ("Vth (V):", "2.0"), ("Vgs (V):", "5")]
            btn_txt = "Calculate Id"
        elif choice == "CMOS Inverter":
            self.fet_cvs.create_line(150, 20, 150, 50, width=2)
            self.fet_cvs.create_oval(145, 45, 155, 55, width=2)
            self.fet_cvs.create_line(130, 55, 170, 55, width=2)
            self.fet_cvs.create_line(150, 55, 150, 80, width=2)
            self.fet_cvs.create_line(130, 80, 170, 80, width=2)
            self.fet_cvs.create_line(150, 80, 150, 130, width=2)
            inputs = [("VDD (V):", "5"), ("Vin (V):", "0")]
            btn_txt = "Evaluate Output"'''

fet_new = '''        if choice == "JFET":
            self.draw_jfet_n(self.fet_cvs, 120, 80)
            inputs = [("Idss (mA):", "10"), ("Vp (V):", "-4"), ("Vgs (V):", "-2")]
            btn_txt = "Calculate Id & gm"
        elif choice == "D-MOSFET":
            self.draw_dmos_n(self.fet_cvs, 120, 80)
            inputs = [("Idss (mA):", "10"), ("Vp (V):", "-4"), ("Vgs (V):", "-2")]
            btn_txt = "Calculate Id & gm"
        elif choice == "E-MOSFET":
            self.draw_emos_n(self.fet_cvs, 120, 80)
            inputs = [("k (mA/V^2):", "0.3"), ("Vth (V):", "2.0"), ("Vgs (V):", "5")]
            btn_txt = "Calculate Id"
        elif choice == "CMOS Inverter":
            self.draw_emos_n(self.fet_cvs, 120, 100) # NMOS
            # Simple PMOS for top
            self.fet_cvs.create_line(120, 50, 130, 50, width=2)
            self.fet_cvs.create_oval(130, 47, 136, 53, width=2) # bubble
            self.fet_cvs.create_line(136, 35, 136, 65, width=2) # gate
            self.fet_cvs.create_line(140, 35, 140, 65, width=3) # channel
            self.fet_cvs.create_line(140, 38, 156, 38, width=2) # source
            self.fet_cvs.create_line(156, 38, 156, 20, width=2) # VDD
            self.fet_cvs.create_line(140, 62, 156, 62, width=2) # drain
            self.fet_cvs.create_line(156, 62, 156, 88, width=2) # to nmos
            self.fet_cvs.create_line(100, 50, 120, 50, width=2) # in
            self.fet_cvs.create_line(100, 100, 120, 100, width=2) # in
            self.fet_cvs.create_line(100, 50, 100, 100, width=2) # in connect
            self.fet_cvs.create_line(156, 75, 180, 75, width=2) # out
            inputs = [("VDD (V):", "5"), ("Vin (V):", "0")]
            btn_txt = "Evaluate Output"'''

code = code.replace(fet_orig, fet_new)

with open("dc_ac_circuits_engine.py", "w", encoding="utf-8") as f:
    f.write(code)
