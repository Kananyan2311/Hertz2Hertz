def get_practical_example(topic):
    examples = {
        "ohms_law": "Practical Application: Sizing a current-limiting resistor for an LED. Example: If you have a 5V supply and a 2V LED that needs 20mA, you use Ohm's Law (R = V/I = (5-2)/0.02 = 150 ohms) to select the right resistor so the LED doesn't burn out.",
        "equiv_res": "Practical Application: Creating a specific resistance value not available off-the-shelf. Example: If you need exactly 50 ohms for impedance matching in an RF circuit, you can place two standard 100 ohm resistors in parallel.",
        "kvl": "Practical Application: Analyzing complex multi-loop circuits like a Wheatstone bridge. Example: Using KVL to determine the exact voltage drop across an RTD (temperature sensor) in a bridge circuit to ensure accurate readings.",
        "ac_rlc": "Practical Application: Designing frequency-selective filters. Example: Tuning an RLC circuit to resonate at 88MHz to 108MHz to act as a bandpass filter for an FM radio receiver.",
        "diode": "Practical Application: Polarity protection in power supplies. Example: Placing a 1N4001 diode in series with a battery input ensures that if a user inserts the battery backwards, the circuit won't be destroyed.",
        "bjt": "Practical Application: Designing audio pre-amplifiers or simple switches. Example: Using a 2N3904 NPN transistor in a common-emitter configuration to amplify a weak microphone signal into a level suitable for a power amplifier.",
        "fet": "Practical Application: High-impedance buffering and power switching. Example: Using a MOSFET to switch a high-current DC motor on and off using a low-current signal from a microcontroller like an Arduino.",
        "logic_gates": "Practical Application: Creating basic control logic without microcontrollers. Example: Using an AND gate to ensure a machine only turns on if both the 'Power' switch AND the 'Safety Guard' switch are closed.",
        "kmap": "Practical Application: Minimizing digital logic to reduce chip area and cost. Example: Simplifying a complex 4-variable truth table into just two logic gates, saving space on a custom PCB.",
        "seq": "Practical Application: Storing state or creating clock dividers. Example: Using a D flip-flop to debounce a push-button switch, ensuring a single clean edge is sent to a digital counter."
    }
    return examples.get(topic, "Practical Application: General circuit analysis and design validation.")
