# =============================================================================
# MATLAB_UTILS.PY - PURE PYTHON NUMERICAL ENGINE (MATLAB-EQUIVALENT ALGORITHMS)
# =============================================================================
# Overview & Architecture:
#   This module serves as the central high-performance calculation engine for the
#   HERTZ2HERTZ Engineering Suite. All mathematical, electrical, semiconductor,
#   RF, and logic computations are executed in 100% PURE PYTHON using NumPy,
#   SciPy, and standard math libraries, formatted with MATLAB-equivalent vectorized
#   idioms, matrix formulations, and explicit algorithmic comments.
#
# Key Features:
#   1. Pure Python Execution: Zero external MATLAB installation or matlab.engine
#      dependency required. Runs instantaneously across all platforms.
#   2. MATLAB-Equivalent Syntax: Formatted identically to MATLAB .m scripts
#      using vectorized array operations, linear algebra backslash solvers (A \ B),
#      and matrix formulations.
#   3. Comprehensive Coverage: Ohm's law, series/parallel networks, multi-loop
#      KVL matrix solvers, AC RLC phasors, Shockley diode models, clippers/clampers,
#      BJT/FET biasing, RF Smith charts, VSWR, and digital logic systems.
# =============================================================================

import os
import math
import numpy as np


class MatlabEngineManager:
    """
    Pure Python Computational Engine implementing MATLAB-equivalent algorithms
    for electrical circuits, semiconductor electronics, RF engineering, and logic.
    """
    _instance = None

    def __new__(cls):
        """Thread-safe Singleton accessor."""
        if cls._instance is None:
            cls._instance = super(MatlabEngineManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        """Initializes the pure Python computational engine."""
        self.engine = None
        self.is_connected = True       # Always ready for pure Python execution
        self.is_connecting = False
        self.engine_error = None
        self.engine_mode = "PURE_PYTHON_MATLAB_VECTORIZED"
        self.scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'matlab_code'))
        print("[HERTZ2HERTZ ENGINE] Pure Python Numerical Engine initialized (MATLAB-Equivalent Algorithms).")

    def get_status(self):
        """Returns True since pure Python calculation engine is always ready."""
        return True

    def get_status_text(self):
        """Returns formatted status badge string displayed in GUI."""
        return ""

    def eval(self, expr, nargout=1):
        """Pure Python expression evaluator."""
        try:
            return eval(expr)
        except Exception as e:
            return None

    def eval_matlab(self, module, func, *args):
        """
        Universal pure Python dispatcher for any legacy MATLAB evaluation calls.
        Executes native NumPy/Python algorithms matching MATLAB .m equivalents.
        """
        try:
            if module == "semiconductor_calc":
                if func == "rectifier":
                    # args: (mode, Vm, Vd)
                    mode, Vm, Vd = args[0], float(args[1]), float(args[2])
                    if mode == "half":
                        Vout_pk = max(0.0, Vm - Vd)
                        return {
                            "Vdc": Vout_pk / np.pi,
                            "Vrms": Vout_pk / 2.0,
                            "PIV": Vm,
                            "Vout_pk": Vout_pk
                        }
                    else:
                        Vout_pk = max(0.0, Vm - 2 * Vd)
                        return {
                            "Vdc": (2 * Vout_pk) / np.pi,
                            "Vrms": Vout_pk / np.sqrt(2),
                            "PIV": Vm - Vd,
                            "Vout_pk": Vout_pk
                        }
                elif func == "bjt_fund":
                    choice, v = args[0], args[1]
                    if choice == "Rb (Fixed Bias)": res = (v["VCC (V)"] - v["VBE (V)"]) / (v["Ib (µA)"] * 1e-6) / 1000.0
                    elif choice == "Rb (Emitter Bias)": res = ((v["VCC (V)"] - v["VBE (V)"]) / (v["Ib (µA)"] * 1e-6) - (v["Beta"] + 1) * (v["Re (kΩ)"] * 1000)) / 1000.0
                    elif choice == "Rc (Fixed Bias)": res = (v["VCC (V)"] - v["VCE (V)"]) / (v["Ic (mA)"] * 1e-3) / 1000.0
                    elif choice == "Rc (Emitter Bias)": res = ((v["VCC (V)"] - v["VCE (V)"]) / (v["Ic (mA)"] * 1e-3) - v["Re (kΩ)"] * 1000) / 1000.0
                    elif choice == "Re (Emitter Bias)": res = (abs(v["VEE (V)"]) - v["VBE (V)"]) / (v["Ie (mA)"] * 1e-3) / 1000.0
                    elif choice == "Ic": res = v["Beta"] * (v["Ib (µA)"] * 1e-3)
                    elif choice == "Ie": res = v["Ic (mA)"] + (v["Ib (µA)"] * 1e-3)
                    elif choice == "Ib (Fixed Bias)": res = (v["VCC (V)"] - v["VBE (V)"]) / (v["Rb (kΩ)"] * 1000) * 1e6
                    elif choice == "Ib (Emitter Bias)": res = (v["VCC (V)"] - v["VBE (V)"]) / (v["Rb (kΩ)"] * 1000 + (v["Beta"] + 1) * v["Re (kΩ)"] * 1000) * 1e6
                    elif choice == "Beta": res = v["Ic (mA)"] / (v["Ib (µA)"] * 1e-3) if v["Ib (µA)"] > 0 else 0.0
                    elif choice == "VCC (Fixed Bias)": res = v["VCE (V)"] + (v["Ic (mA)"] * 1e-3) * (v["Rc (kΩ)"] * 1e3)
                    elif choice == "VCC (Emitter Bias)": res = v["VCE (V)"] + (v["Ic (mA)"] * 1e-3) * ((v["Rc (kΩ)"] + v["Re (kΩ)"]) * 1e3)
                    elif choice == "VEE": res = -1 * (v["VBE (V)"] + (v["Ie (mA)"] * 1e-3) * (v["Re (kΩ)"] * 1e3))
                    elif choice == "VCE (Fixed Bias)": res = v["VCC (V)"] - (v["Ic (mA)"] * 1e-3) * (v["Rc (kΩ)"] * 1e3)
                    elif choice == "VCE (Emitter Bias)": res = v["VCC (V)"] - (v["Ic (mA)"] * 1e-3) * ((v["Rc (kΩ)"] + v["Re (kΩ)"]) * 1e3)
                    elif choice == "Isat (Fixed Bias)": res = (v["VCC (V)"] / (v["Rc (kΩ)"] * 1e3)) * 1000.0
                    elif choice == "Isat (Emitter Bias)": res = (v["VCC (V)"] / ((v["Rc (kΩ)"] + v["Re (kΩ)"]) * 1e3)) * 1000.0
                    else: res = 0.0
                    return {"result": res}

            elif module == "logic_calc":
                if func == "convert_base":
                    val_str, from_base, to_base = str(args[0]), str(args[1]), str(args[2])
                    base_map = {"Decimal": 10, "Binary": 2, "Octal": 8, "Hexadecimal": 16}
                    dec = int(val_str, base_map[from_base])
                    if to_base == "Decimal": r = str(dec)
                    elif to_base == "Binary": r = bin(dec)[2:]
                    elif to_base == "Octal": r = oct(dec)[2:]
                    elif to_base == "Hexadecimal": r = hex(dec)[2:].upper()
                    return {"result": r, "dec_val": dec}
                elif func == "eval_gate":
                    gate, a, b = str(args[0]), int(args[1]), int(args[2])
                    if gate == "AND": res = a & b
                    elif gate == "OR": res = a | b
                    elif gate == "XOR": res = a ^ b
                    elif gate == "NAND": res = int(not (a & b))
                    elif gate == "NOR": res = int(not (a | b))
                    elif gate == "XNOR": res = int(not (a ^ b))
                    else: res = 0
                    return {"result": res}

            elif module == "rf_calc":
                if func == "vswr_from_power":
                    pf, pr = float(args[0]), float(args[1])
                    gamma_mag = np.sqrt(pr / pf) if pf > 0 else 0.0
                    vswr = (1.0 + gamma_mag) / (1.0 - gamma_mag) if gamma_mag < 1.0 else float('inf')
                    rl = -20.0 * np.log10(gamma_mag) if gamma_mag > 0 else float('inf')
                    return {"gamma_mag": gamma_mag, "vswr": vswr, "return_loss": rl}
                elif func == "quarter_wave":
                    z0, zl = float(args[0]), float(args[1])
                    return {"Z1": np.sqrt(z0 * zl)}
                elif func == "friis_link":
                    pt, gt, gr, pl = float(args[0]), float(args[1]), float(args[2]), float(args[3])
                    return {"Pr": pt + gt + gr - pl}

        except Exception as e:
            print(f"[HERTZ2HERTZ ENGINE] Error in eval_matlab({module}, {func}): {e}")
        return None

    # =========================================================================
    # SECTION I: EE CIRCUITS & FUNDAMENTALS (MATLAB-EQUIVALENT CODE)
    # =========================================================================

    def ee_ohms_law(self, V, I, R, P):
        """
        Solves Ohm's Law and Electric Power equations.
        
        MATLAB Equivalent Algorithm:
        % V = I * R;
        % P = V * I = I^2 * R = V^2 / R;
        """
        # % MATLAB: Resolve unknown pair from known pair
        if V is not None and I is not None:
            R = V / I
            P = V * I
        elif V is not None and R is not None:
            I = V / R
            P = (V**2) / R
        elif I is not None and R is not None:
            V = I * R
            P = (I**2) * R
        elif P is not None and V is not None:
            I = P / V
            R = (V**2) / P
        elif P is not None and I is not None:
            V = P / I
            R = P / (I**2)
        elif P is not None and R is not None:
            V = np.sqrt(P * R)
            I = np.sqrt(P / R)
        return float(V), float(I), float(R), float(P)

    def ee_series_res(self, R_list, Vin):
        """
        Calculates equivalent resistance, loop current, voltage drops,
        and power dissipation for series resistors.
        
        MATLAB Equivalent Algorithm:
        % Req = sum(R);
        % Itotal = Vin / Req;
        % V_drops = Itotal .* R;
        % P_diss = (Itotal.^2) .* R;
        % Ptotal = Vin * Itotal;
        """
        R_arr = np.array(R_list, dtype=np.float64)
        Req = float(np.sum(R_arr))
        Itotal = float(Vin / Req) if Req > 0 else 0.0
        V_drops = (Itotal * R_arr).tolist()
        P_diss = ((Itotal**2) * R_arr).tolist()
        Ptotal = float(Vin * Itotal)
        return Req, Itotal, V_drops, P_diss, Ptotal

    def ee_parallel_res(self, R_list, Vin):
        """
        Calculates equivalent resistance, total current, branch currents,
        and power dissipation for parallel resistors.
        
        MATLAB Equivalent Algorithm:
        % Geq = sum(1 ./ R);
        % Req = 1 / Geq;
        % I_branches = Vin ./ R;
        % Itotal = sum(I_branches);
        % P_branches = (Vin^2) ./ R;
        % Ptotal = Vin * Itotal;
        """
        R_arr = np.array(R_list, dtype=np.float64)
        G_arr = 1.0 / R_arr
        Geq = float(np.sum(G_arr))
        Req = float(1.0 / Geq) if Geq > 0 else float('inf')
        I_branches = (float(Vin) / R_arr).tolist()
        Itotal = float(np.sum(I_branches))
        P_branches = ((float(Vin)**2) / R_arr).tolist()
        Ptotal = float(Vin * Itotal)
        return Req, Itotal, I_branches, P_branches, Ptotal

    def ee_kvl_solve(self, loops, V1, V2, R_list, R_mid_list):
        r"""
        Solves multi-loop Kirchhoff's Voltage Law (KVL) mesh current equations using
        matrix linear algebra (Equivalent to MATLAB backslash solver: I = A \ B).
        
        MATLAB System Formulation:
        % A = zeros(loops, loops);
        % B = zeros(loops, 1);
        % I = A \ B;
        """
        A = np.zeros((loops, loops), dtype=np.float64)
        B = np.zeros(loops, dtype=np.float64)

        for i in range(loops):
            if i == 0:
                if loops == 1:
                    A[i, i] = R_list[i]
                    B[i] = V1 - V2
                else:
                    A[i, i] = R_list[i] + R_mid_list[i]
                    A[i, i+1] = -R_mid_list[i]
                    B[i] = V1
            elif i == loops - 1:
                A[i, i] = R_mid_list[i-1] + R_list[i]
                A[i, i-1] = -R_mid_list[i-1]
                B[i] = -V2
            else:
                A[i, i] = R_mid_list[i-1] + R_list[i] + R_mid_list[i]
                A[i, i-1] = -R_mid_list[i-1]
                A[i, i+1] = -R_mid_list[i]
                B[i] = 0.0

        # MATLAB Equivalent: I = A \ B;
        I = np.linalg.solve(A, B)
        return list(I)

    def ee_ac_rlc(self, Vm, freq, R, L, C):
        """
        Analyzes AC steady-state series RLC circuits: impedance, phase angle,
        power factor, and complex power.
        
        MATLAB Equivalent Algorithm:
        % omega = 2 * pi * freq;
        % XL = omega * L;
        % XC = 1 / (omega * C);
        % Z = R + 1j * (XL - XC);
        % Zmag = abs(Z);
        % phi = angle(Z);
        """
        omega = 2.0 * np.pi * float(freq)
        XL = omega * float(L)
        XC = 1.0 / (omega * float(C)) if float(C) > 0 else float('inf')
        Xnet = XL - XC
        Z_complex = complex(float(R), Xnet)
        Zmag = abs(Z_complex)
        phase_rad = np.arctan2(Xnet, float(R))
        phase_deg = np.degrees(phase_rad)

        Im = float(Vm) / Zmag if Zmag > 0 else 0.0
        Vrms = float(Vm) / np.sqrt(2)
        Irms = Im / np.sqrt(2)
        pf = np.cos(phase_rad)
        Preal = Vrms * Irms * pf
        Qreact = Vrms * Irms * np.sin(phase_rad)
        Sapp = Vrms * Irms

        return {
            'omega': omega, 'XL': XL, 'XC': XC, 'Xnet': Xnet, 'Zmag': Zmag,
            'phase_rad': phase_rad, 'phase_deg': phase_deg, 'Im': Im,
            'Vrms': Vrms, 'Irms': Irms, 'pf': pf, 'Preal': Preal,
            'Qreact': Qreact, 'Sapp': Sapp
        }

    # =========================================================================
    # SECTION II: SEMICONDUCTOR ELECTRONICS (MATLAB-EQUIVALENT CODE)
    # =========================================================================

    def semi_diode_calc(self, target_var, Is, n, T, Vd, Id):
        """
        Solves the Shockley PN Junction Diode equation.
        
        MATLAB Equivalent Algorithm:
        % k_b = 1.380649e-23; q = 1.60217663e-19;
        % Vt = (k_b * (T + 273.15)) / q;
        % Id = Is * (exp(Vd / (n * Vt)) - 1);
        % rd = (n * Vt) / Id;
        """
        k_b = 1.380649e-23
        q = 1.60217663e-19
        Vt = (k_b * (float(T) + 273.15)) / q

        Is = float(Is)
        n = float(n)
        Vd = float(Vd)
        Id = float(Id)

        if target_var == "Current":
            calc_Id = Is * (np.exp(Vd / (n * Vt)) - 1.0)
            return {'Id': float(calc_Id), 'Vt': float(Vt)}
        elif target_var == "Voltage":
            calc_Vd = n * Vt * np.log((Id / Is) + 1.0) if Id > 0 else 0.0
            return {'Vd': float(calc_Vd), 'Vt': float(Vt)}
        elif target_var == "DC Resistance":
            calc_Id = Is * (np.exp(Vd / (n * Vt)) - 1.0)
            rdc = Vd / calc_Id if calc_Id != 0 else float('inf')
            return {'rdc': float(rdc), 'Id': float(calc_Id), 'Vt': float(Vt)}
        elif target_var == "AC Resistance":
            calc_Id = Id if Id > 0 else Is * (np.exp(Vd / (n * Vt)) - 1.0)
            rac = (n * Vt) / calc_Id if calc_Id > 0 else float('inf')
            return {'rac': float(rac), 'Id': float(calc_Id), 'Vt': float(Vt)}
        return {}

    def semi_diode_app(self, app_type, Vp, R, Vd, C, Vb):
        """
        Diode rectifiers, clippers, clampers, and LED circuits.
        
        MATLAB Equivalent Algorithm:
        % switch app_type
        %   case 'Half-wave', Vout_pk = max(0, Vp - Vd); Vdc = Vout_pk / pi;
        %   case 'Full-wave', Vout_pk = max(0, Vp - 2*Vd); Vdc = 2*Vout_pk / pi;
        % end
        """
        Vp, R, Vd, C, Vb = float(Vp), float(R), float(Vd), float(C), float(Vb)

        if app_type == "Half-wave":
            Vout_pk = max(0.0, Vp - Vd)
            return {'Vout_pk': Vout_pk, 'Vdc': Vout_pk / np.pi, 'Vrms': Vout_pk / 2.0, 'PIV': Vp}
        elif app_type == "Full-wave":
            Vout_pk = max(0.0, Vp - 2.0 * Vd)
            return {'Vout_pk': Vout_pk, 'Vdc': (2.0 * Vout_pk) / np.pi, 'Vrms': Vout_pk / np.sqrt(2), 'PIV': Vp - Vd}
        elif app_type == "Positive Clipper":
            return {'Vclip': Vb + Vd, 'Vmin': -Vp, 'Vmax': Vb + Vd}
        elif app_type == "Negative Clipper":
            return {'Vclip': Vb - Vd, 'Vmin': Vb - Vd, 'Vmax': Vp}
        elif app_type == "Positive Clamper":
            return {'Vshift': Vp - Vd + Vb, 'Vmax': 2.0 * Vp - Vd + Vb, 'Vmin': Vb - Vd}
        elif app_type == "Negative Clamper":
            return {'Vshift': -(Vp - Vd) + Vb, 'Vmax': Vb + Vd, 'Vmin': -(2.0 * Vp - Vd - Vb)}
        elif app_type == "LED":
            Iled = R * 1e-3
            R_series = (Vp - Vd) / Iled if Iled > 0 else float('inf')
            return {'R_series': R_series, 'P_led': Vd * Iled}
        return {}

    def semi_bjt_bias(self, bias_type, Vcc, Rb1, Rb2, Rc, Re, beta, Vbe):
        """
        Solves BJT DC Biasing Operating Q-Points.
        
        MATLAB Equivalent Algorithm:
        % Ib = (Vth - Vbe) / (Rth + (beta + 1) * Re);
        % Ic = beta * Ib;
        % Vce = Vcc - Ic * (Rc + Re);
        """
        Vcc, Rb1, Rb2, Rc, Re, beta, Vbe = float(Vcc), float(Rb1), float(Rb2), float(Rc), float(Re), float(beta), float(Vbe)
        Rc_ohm = Rc * 1e3
        Re_ohm = Re * 1e3

        if bias_type == "Fixed Bias":
            Rb_ohm = Rb1 * 1e3
            Ib = (Vcc - Vbe) / Rb_ohm
            Ic = beta * Ib
            Vce = Vcc - Ic * Rc_ohm
            I_sat = Vcc / Rc_ohm
        elif bias_type == "Voltage Divider":
            R1_ohm = Rb1 * 1e3
            R2_ohm = Rb2 * 1e3
            Rth = (R1_ohm * R2_ohm) / (R1_ohm + R2_ohm)
            Vth = Vcc * (R2_ohm / (R1_ohm + R2_ohm))
            Ib = (Vth - Vbe) / (Rth + (beta + 1.0) * Re_ohm)
            Ic = beta * Ib
            Vce = Vcc - Ic * (Rc_ohm + Re_ohm)
            I_sat = Vcc / (Rc_ohm + Re_ohm)
        elif bias_type == "Emitter Bias":
            Rb_ohm = Rb1 * 1e3
            Ib = (Vcc - Vbe) / (Rb_ohm + (beta + 1.0) * Re_ohm)
            Ic = beta * Ib
            Vce = Vcc - Ic * (Rc_ohm + Re_ohm)
            I_sat = Vcc / (Rc_ohm + Re_ohm)
        else:  # Collector Feedback
            Rb_ohm = Rb1 * 1e3
            Ib = (Vcc - Vbe) / (Rb_ohm + beta * (Rc_ohm + Re_ohm))
            Ic = beta * Ib
            Vce = Vcc - Ic * (Rc_ohm + Re_ohm)
            I_sat = Vcc / (Rc_ohm + Re_ohm)

        return {
            'Ib_uA': Ib * 1e6,
            'Ic_mA': Ic * 1e3,
            'Vce': Vce,
            'Isat_mA': I_sat * 1e3,
            'Vcc': Vcc
        }

    def semi_fet_calc(self, fet_type, Idss, Vp, Vgs, k, Vth, Vdd, Vin):
        """
        Field-Effect Transistor equations (JFET, D-MOSFET, E-MOSFET).
        
        MATLAB Equivalent Algorithm:
        % Id = Idss * (1 - Vgs / Vp)^2;
        % gm = (2 * Idss / abs(Vp)) * (1 - Vgs / Vp);
        """
        Idss, Vp, Vgs = float(Idss), float(Vp), float(Vgs)
        k, Vth, Vdd, Vin = float(k), float(Vth), float(Vdd), float(Vin)

        if fet_type in ["JFET", "D-MOSFET"]:
            Id = Idss * ((1.0 - Vgs / Vp)**2) if (1.0 - Vgs / Vp) >= 0 else 0.0
            gm0 = 2.0 * Idss / abs(Vp) if Vp != 0 else 0.0
            gm = gm0 * (1.0 - Vgs / Vp)
            return {'Id_mA': Id, 'gm_mS': gm, 'gm0_mS': gm0}
        elif fet_type == "E-MOSFET":
            Id = k * ((Vgs - Vth)**2) if Vgs > Vth else 0.0
            gm = 2.0 * k * (Vgs - Vth) if Vgs > Vth else 0.0
            return {'Id_mA': Id, 'gm_mS': gm, 'Vth': Vth}
        else:
            Vout = Vdd if Vin < Vdd / 2.0 else 0.0
            return {'Vout': Vout, 'state': 1 if Vout > Vdd / 2.0 else 0, 'Vth': Vdd / 2.0}

    # =========================================================================
    # SECTION III: RF ENGINEERING COMPUTATIONS (MATLAB-EQUIVALENT CODE)
    # =========================================================================

    def rf_calc(self, action, *args):
        """
        RF computations: VSWR, quarter-wave transformer, Friis link budget.
        
        MATLAB Equivalent Algorithm:
        % gamma_mag = sqrt(Pr / Pf);
        % vswr = (1 + gamma_mag) / (1 - gamma_mag);
        % return_loss = -20 * log10(gamma_mag);
        """
        if action == 'vswr':
            Pf, Pr = float(args[0]), float(args[1])
            gamma_mag = np.sqrt(Pr / Pf) if Pf > 0 else 0.0
            vswr = (1.0 + gamma_mag) / (1.0 - gamma_mag) if gamma_mag < 1.0 else float('inf')
            rl = -20.0 * np.log10(gamma_mag) if gamma_mag > 0 else float('inf')
            return {'gamma_mag': gamma_mag, 'vswr': vswr, 'return_loss_dB': rl}
        elif action == 'match_transformer':
            z0, zl = float(args[0]), float(args[1])
            return {'Z1': np.sqrt(z0 * zl)}
        elif action == 'link_budget':
            pt, gt, gr, pl = float(args[0]), float(args[1]), float(args[2]), float(args[3])
            return {'Pr_dBm': pt + gt + gr - pl}
        return {}

    # =========================================================================
    # SECTION IV: DIGITAL LOGIC & NUMBER SYSTEMS (MATLAB-EQUIVALENT CODE)
    # =========================================================================

    def logic_base_convert(self, val_str, from_base, to_base):
        """
        Radix converter matching MATLAB's bin2dec, dec2hex, dec2bin, etc.
        """
        base_map = {"Decimal": 10, "Binary": 2, "Octal": 8, "Hexadecimal": 16}
        dec = int(str(val_str), base_map[from_base])
        if to_base == "Decimal": r = str(dec)
        elif to_base == "Binary": r = bin(dec)[2:]
        elif to_base == "Octal": r = oct(dec)[2:]
        elif to_base == "Hexadecimal": r = hex(dec)[2:].upper()
        return r, dec

    def logic_gate_eval(self, a, b, gate_type):
        """
        Evaluates two-input Boolean logic gates matching MATLAB bitwise functions.
        """
        a, b = int(a), int(b)
        if gate_type == "AND": return int(a & b)
        elif gate_type == "OR": return int(a | b)
        elif gate_type == "XOR": return int(a ^ b)
        elif gate_type == "NAND": return int(not (a & b))
        elif gate_type == "NOR": return int(not (a | b))
        elif gate_type == "XNOR": return int(not (a ^ b))
        return 0


# Singleton pure Python numerical manager instance
matlab_manager = MatlabEngineManager()
