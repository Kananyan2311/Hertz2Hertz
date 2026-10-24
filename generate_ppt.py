import collections
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os

def create_presentation():
    prs = Presentation()
    
    # Define slide content
    slides_data = [
        {
            "title": "BOOT SEQUENCE: INITIATED (HERTZ2HERTZ v1.0)",
            "visuals": "- Background: Pastel Summer Sky Cyan (#BAE6FD)\n- Elements: Lemon Tang Bubble Logo, HERTZ2HERTZ title banner in Sunshine Lemon Yellow with stark 4px black borders and zero corner radii.\n- Graphics: Top barcode graphic: ║▌║█║▌│║▌║▌█║ HERTZ2HERTZ • LEMON BEACH EDITION • 2ND MINI ALBUM",
            "checklist": "N/A (Introduction)",
            "script": "\"Welcome, everyone. Today, Steven and I (Ivan) are presenting our final project: HERTZ2HERTZ. We've built an extensive Engineering Simulation Suite designed entirely around a 'Retro Lemon Beach' Neobrutalist aesthetic—think '90s desktop operating systems mixed with a summer K-Pop photobook concept. But beneath the bright cyan and yellow UI lies a massive mathematical engine. Let's boot up the system.\""
        },
        {
            "title": "DIRECTORIES & DIRECTIVES: THE CALCULATION SCOPE",
            "visuals": "- Background: Mint Seafoam Green (#A7F3D0)\n- Elements: Four chunky '90s folder icons (EE Fundamentals, DC/AC Circuits, RF Toolbox, Logic Synth).\n- Graphics: Notepad showing KVL Matrix math ([R][I] = [V]) and AC Impedance formulas rendered in Courier New font.",
            "checklist": "Checklist #1: Problem & Topic Selection",
            "script": "\"We scoped our application to tackle the heavy-lifting mathematics of a BSCPE curriculum. The calculator isn't just doing basic arithmetic; it executes complex engineering computations. We cover EE Fundamentals like Ohm's Law and Series/Parallel Equivalent Resistance, multi-loop Kirchhoff (KVL) matrix solving, steady-state AC RLC circuits, RF Engineering, and Logic Circuits. Every module rigorously implements the textbook matrix algebra and calculus required for these domains.\""
        },
        {
            "title": "BLUEPRINTS: ARCHITECTING THE DESKTOP OS",
            "visuals": "- Background: Coral Flamingo Pink (#FBCFE8)\n- Elements: Wireframes showing Lock Screen transitioning to Desktop Workspace.\n- Graphics: Arrows showing left-side navigation sidebar pointing to the right-side CTkScrollableFrame content area.",
            "checklist": "Checklist #2: GUI Wireframing & Layout",
            "script": "\"To house all these calculators, we didn't just build a window; we wireframed an entire retro operating system. The user journey starts at a Lock Screen with profile selectors, which transitions into a Desktop Workspace. Inside individual apps, we utilized a rigid grid layout: a fixed left sidebar for navigation and a scrollable content frame on the right. This ensures that even our most complex KVL matrix inputs never look cramped.\""
        },
        {
            "title": "PIXEL PUSHING: CUSTOMTKINTER CONSTRUCTION",
            "visuals": "- Background: Sunshine Lemon Yellow (#FEF08A)\n- Elements: Snippets of CustomTkinter code: ctk.CTkButton(corner_radius=0, border_width=4, border_color=\"#000000\").\n- Graphics: Close-ups of chunky CustomTkinter UI widgets (Buttons, CTkComboBoxes, CTkCanvas drawings).",
            "checklist": "Checklist #3: Interface Development",
            "script": "\"For the frontend, we pushed the CustomTkinter library to its limits. To achieve true Neobrutalism, we stripped away all modern styling—forcing corner_radius=0, implementing stark 4px solid black borders, and overriding default palettes with web-safe pastel hex codes like Lemon Yellow and Seafoam Green. We also used native Tkinter Canvas to hard-code dynamic circuit schematics directly into the UI, making the app highly visual without relying on external image files.\""
        },
        {
            "title": "UNDER THE HOOD: THE MATLAB MANAGER",
            "visuals": "- Background: Pastel Summer Sky Cyan (#BAE6FD)\n- Elements: Flowchart showing event-driven push callback: Python UI Button -> matlab_manager -> ee_calc.m (MATLAB Engine) -> Python UI Label.\n- Graphics: Highlight the live MATLAB Engine status taskbar badge [MATLAB: INITIALIZING...].",
            "checklist": "Checklist #4: Underlying Logic & Callbacks",
            "script": "\"The true power of HERTZ2HERTZ is its dual-engine architecture. Python and CustomTkinter handle the event-driven UI flawlessly, but when you click 'Calculate', the math is dispatched via our custom matlab_manager script. This bridges Python with the official R2026b MATLAB Engine, passing matrices to native .m files in the backend. We even built a live status monitor into the retro taskbar so the user knows exactly when MATLAB has booted and is ready to process.\""
        },
        {
            "title": "BULLETPROOFING: CRASH PREVENTION",
            "visuals": "- Background: Coral Flamingo Pink (#FBCFE8)\n- Elements: Ohm's law input UI next to a red error readout label.\n- Graphics: Code snippets highlighting try-catch blocks intercepting empty strings and zero values.",
            "checklist": "Checklist #5: Input Validation & Error Handling",
            "script": "\"Users do unpredictable things, so our UI has to be bulletproof. Instead of letting MATLAB throw a fatal exception and crash the Python shell, we wrapped all callbacks in strict try-catch validation. For example, in the Ohm's law solver, if a user enters three values instead of two, or leaves a required array empty, Python intercepts the logic, halts the MATLAB dispatch, and updates the terminal UI with a stylized red error message. No crashes, just continuous runtime.\""
        },
        {
            "title": "RENDER MODE: DYNAMIC MATPLOTLIB VISUALS",
            "visuals": "- Background: Mint Seafoam Green (#A7F3D0)\n- Elements: Side-by-side screenshots of FigureCanvasTkAgg plots (V-I Characteristic Line Plot, KVL Loop Current Bar Chart).\n- Graphics: Plots showing #FFF5EE facecolors and #0055FF plotting lines embedded in Tkinter.",
            "checklist": "Checklist #6: Data Visualization & Graphing",
            "script": "\"Engineering requires visualization. We integrated matplotlib directly into the CustomTkinter frames using FigureCanvasTkAgg. These aren't static images; they are dynamically generated every time the MATLAB engine returns an array. Whether it's plotting the linear V-I operating Q-point, generating a parabolic power dissipation curve, or rendering a bar chart of multi-loop KVL currents, the charts automatically re-scale and inject themselves right into the Neobrutalist UI.\""
        },
        {
            "title": "SURFING THE MODULES: THE DESKTOP WORKSPACE",
            "visuals": "- Background: Sunshine Lemon Yellow (#FEF08A)\n- Elements: Animation sequence showing trigger_transition() wipe effect.\n- Graphics: RetroWindow instances hiding and showing as icons are clicked on the Desktop Workspace.",
            "checklist": "Checklist #7: Multi-Tab / Navigation Feature",
            "script": "\"Managing five massive calculators on one screen is a UX nightmare, so we built a multi-tab desktop environment. By wrapping our engine frames in custom RetroWindow classes, we created a seamless workspace. When you switch from the Logic Synth to the RF Toolbox, an animated full-screen color wipe visually covers the screen, safely un-packing the old GUI and packing the new one. It gives the user a fresh, clean interface instantly.\""
        },
        {
            "title": "THE LOGBOOK: PERSISTENT MEMORY EXPORT",
            "visuals": "- Background: Pastel Summer Sky Cyan (#BAE6FD)\n- Elements: Snippet of calc_history_log text file showing generated header with student names.\n- Graphics: Green [ EXPORT REPORT (.TXT/.CSV) ] toolbar button.",
            "checklist": "Checklist #8: Export & Report Capabilities",
            "script": "\"Because this is an engineering tool, you need to save your work. Behind the scenes, the application continuously appends timestamped calculation results, matrix outputs, and solved loop currents to an internal string. By clicking the green Export button in the top toolbar, the app generates a formatted .txt or .csv report directly to your drive, complete with the timestamp and our developer signatures, ready to be attached to a lab report.\""
        },
        {
            "title": "SYSTEM CHECK GREEN: DEMO PREP",
            "visuals": "- Background: Deep Black (#000000) with Mint Green (#A7F3D0) text.\n- Elements: Side-by-side verification: MATLAB Desktop terminal output vs. HERTZ2HERTZ GUI output.\n- Graphics: Retro prompt: STATUS: VERIFIED [/] ... INITIATING LIVE DEMONSTRATION.",
            "checklist": "Checklist #9: Testing & UI Verification",
            "script": "\"Before deploying HERTZ2HERTZ, we rigorously stress-tested the integration. We manually verified that the matrix mathematics performed in our Python UI matched the pure MATLAB engine terminal exactly 1-to-1. We've handled the edge cases, ensured the pure-Python fallbacks work when the engine is busy, and confirmed the UI is stable. The system is verified, and we are now ready to jump out of the slides for the live software demonstration.\""
        }
    ]

    for index, slide_info in enumerate(slides_data):
        # Use a blank slide layout
        blank_slide_layout = prs.slide_layouts[5] # Title only
        slide = prs.slides.add_slide(blank_slide_layout)
        
        # Set Title
        title_shape = slide.shapes.title
        title_shape.text = slide_info["title"]
        title_shape.text_frame.paragraphs[0].font.name = 'Arial'
        title_shape.text_frame.paragraphs[0].font.bold = True
        
        # Create Content Box
        left = Inches(0.5)
        top = Inches(1.5)
        width = Inches(9)
        height = Inches(5.5)
        
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        
        # Add Visual Recommendations
        p = tf.add_paragraph()
        p.text = "Visual Recommendations:"
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(0, 51, 153)
        
        p2 = tf.add_paragraph()
        p2.text = slide_info["visuals"]
        p2.font.size = Pt(14)
        p2.space_after = Pt(14)
        
        # Add Checklist Tag
        p3 = tf.add_paragraph()
        p3.text = "Checklist Fulfillment:"
        p3.font.bold = True
        p3.font.size = Pt(18)
        p3.font.color.rgb = RGBColor(0, 102, 0)
        
        p4 = tf.add_paragraph()
        p4.text = slide_info["checklist"]
        p4.font.size = Pt(14)
        p4.font.bold = True
        p4.space_after = Pt(14)
        
        # Add Speaker Script
        p5 = tf.add_paragraph()
        p5.text = "Speaker Script:"
        p5.font.bold = True
        p5.font.size = Pt(18)
        p5.font.color.rgb = RGBColor(153, 0, 51)
        
        p6 = tf.add_paragraph()
        p6.text = slide_info["script"]
        p6.font.size = Pt(16)
        p6.font.italic = True
        
    output_path = r"C:\Users\Kananyan\Desktop\HERTZ2HERTZ_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully saved to {output_path}")

if __name__ == '__main__':
    create_presentation()
