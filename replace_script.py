import sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    content = f.read()

target = """        case 'bjt_fund'
            p = varargin{1};
            s = varargin{2};
            
            switch p
                case 'Ic'
                    beta = s.beta; Ib = s.Ib * 1e-6;
                    val = (beta * Ib) * 1e3; % convert to mA
                    res = struct('val', double(val), 'unit', 'mA');
                case 'Ie'
                    beta = s.beta; Ib = s.Ib * 1e-6;
                    val = ((beta + 1) * Ib) * 1e3; % convert to mA
                    res = struct('val', double(val), 'unit', 'mA');
                case 'Beta'
                    Ic = s.Ic * 1e-3; Ib = s.Ib * 1e-6;
                    val = Ic / Ib;
                    res = struct('val', double(val), 'unit', '');
                case 'Vce'
                    Vcc = s.Vcc; Ic = s.Ic * 1e-3; Rc = s.Rc; Re = s.Re;
                    val = Vcc - Ic * (Rc + Re);
                    res = struct('val', double(val), 'unit', 'V');
                case 'Rb'
                    Vcc = s.Vcc; Vbe = s.Vbe; Ib = s.Ib * 1e-6;
                    val = ((Vcc - Vbe) / Ib) * 1e-3; % in kOhms
                    res = struct('val', double(val), 'unit', 'kIc');
                case 'Rc'
                    Vcc = s.Vcc; Vce = s.Vce; Ic = s.Ic * 1e-3; Re = s.Re;
                    val = ((Vcc - Vce - Ic * Re) / Ic) * 1e-3;
                    res = struct('val', double(val), 'unit', 'kIc');
                case 'Isat'
                    Vcc = s.Vcc; Rc = s.Rc; Re = s.Re;
                    val = (Vcc / (Rc + Re)) * 1e3; % in mA
                    res = struct('val', double(val), 'unit', 'mA');
                otherwise
                    res = struct('val', 0.0, 'unit', '');
            end"""

replacement = """        case 'bjt_fund'
            choice = varargin{1};
            v = varargin{2};
            
            switch choice
                case 'Rb (Fixed Bias)'
                    val = (v.Vcc - v.Vbe) / (v.Ib * 1e-6) / 1000.0;
                    res = struct('val', double(val), 'unit', 'kOhm');
                case 'Rb (Emitter Bias)'
                    val = ((v.Vcc - v.Vbe) / (v.Ib * 1e-6) - (v.beta + 1) * (v.Re * 1000)) / 1000.0;
                    res = struct('val', double(val), 'unit', 'kOhm');
                case 'Rc (Fixed Bias)'
                    val = (v.Vcc - v.Vce) / (v.Ic * 1e-3) / 1000.0;
                    res = struct('val', double(val), 'unit', 'kOhm');
                case 'Rc (Emitter Bias)'
                    val = ((v.Vcc - v.Vce) / (v.Ic * 1e-3) - v.Re * 1000) / 1000.0;
                    res = struct('val', double(val), 'unit', 'kOhm');
                case 'Re (Emitter Bias)'
                    val = (abs(v.Vee) - v.Vbe) / (v.Ie * 1e-3) / 1000.0;
                    res = struct('val', double(val), 'unit', 'kOhm');
                case 'Ic'
                    val = v.beta * (v.Ib * 1e-3);
                    res = struct('val', double(val), 'unit', 'mA');
                case 'Ie'
                    val = v.Ic + (v.Ib * 1e-3);
                    res = struct('val', double(val), 'unit', 'mA');
                case 'Ib (Fixed Bias)'
                    val = (v.Vcc - v.Vbe) / (v.Rb * 1000) * 1e6;
                    res = struct('val', double(val), 'unit', 'uA');
                case 'Ib (Emitter Bias)'
                    val = (v.Vcc - v.Vbe) / (v.Rb * 1000 + (v.beta + 1) * v.Re * 1000) * 1e6;
                    res = struct('val', double(val), 'unit', 'uA');
                case 'Beta'
                    if v.Ib > 0
                        val = v.Ic / (v.Ib * 1e-3);
                    else
                        val = 0.0;
                    end
                    res = struct('val', double(val), 'unit', '');
                case 'VCC (Fixed Bias)'
                    val = v.Vce + (v.Ic * 1e-3) * (v.Rc * 1e3);
                    res = struct('val', double(val), 'unit', 'V');
                case 'VCC (Emitter Bias)'
                    val = v.Vce + (v.Ic * 1e-3) * ((v.Rc + v.Re) * 1e3);
                    res = struct('val', double(val), 'unit', 'V');
                case 'VEE'
                    val = -1 * (v.Vbe + (v.Ie * 1e-3) * (v.Re * 1e3));
                    res = struct('val', double(val), 'unit', 'V');
                case 'VCE (Fixed Bias)'
                    val = v.Vcc - (v.Ic * 1e-3) * (v.Rc * 1e3);
                    res = struct('val', double(val), 'unit', 'V');
                case 'VCE (Emitter Bias)'
                    val = v.Vcc - (v.Ic * 1e-3) * ((v.Rc + v.Re) * 1e3);
                    res = struct('val', double(val), 'unit', 'V');
                case 'Isat (Fixed Bias)'
                    val = (v.Vcc / (v.Rc * 1e3)) * 1000.0;
                    res = struct('val', double(val), 'unit', 'mA');
                case 'Isat (Emitter Bias)'
                    val = (v.Vcc / ((v.Rc + v.Re) * 1e3)) * 1000.0;
                    res = struct('val', double(val), 'unit', 'mA');
                otherwise
                    res = struct('val', 0.0, 'unit', '');
            end"""

new_content = content.replace(target, replacement)
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    f.write(new_content)

