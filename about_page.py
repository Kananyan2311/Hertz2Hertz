import customtkinter as ctk
import os
from PIL import Image
from retro_ui import RETRO_FONT, TITLE_FONT

class AboutPage(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # TITLE BANNER (Neobrutalist)
        title_frame = ctk.CTkFrame(self, fg_color="#FF3333", border_width=4, border_color="#000000", corner_radius=0)
        title_frame.grid(row=0, column=0, pady=(20, 25), padx=40, sticky="ew")
        
        ctk.CTkLabel(
            title_frame, 
            text="DEVELOPER PROFILES & CREDITS", 
            font=("Helvetica", 26, "bold"), 
            text_color="#FFFFFF"
        ).pack(padx=20, pady=12)
        
        # ID CARDS CONTAINER
        id_container = ctk.CTkFrame(self, fg_color="transparent")
        id_container.grid(row=1, column=0, pady=10, padx=20)
        
        # Load developer profile photos
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dev1_path = os.path.join(base_dir, "assets", "user_uploaded_dev.jpg")
        dev2_path = os.path.join(base_dir, "assets", "steven.png")
        
        # --- ID CARD 1: Lead Engineer ---
        card1 = ctk.CTkFrame(
            id_container, 
            fg_color="#F5F5F0", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            width=360, 
            height=490
        )
        card1.grid(row=0, column=0, padx=25, pady=10)
        card1.pack_propagate(False)
        
        # Header strip
        c1_head = ctk.CTkFrame(card1, fg_color="#0055FF", border_width=0, corner_radius=0, height=42)
        c1_head.pack(fill="x")
        c1_head.pack_propagate(False)
        ctk.CTkLabel(c1_head, text="NU LAGUNA", font=("Helvetica", 14, "bold"), text_color="#FFFFFF").pack(expand=True)
        
        # Photo Frame
        photo1_frame = ctk.CTkFrame(card1, fg_color="#FFFFFF", border_width=3, border_color="#000000", corner_radius=0, width=170, height=170)
        photo1_frame.pack(pady=18)
        photo1_frame.pack_propagate(False)
        
        if os.path.exists(dev1_path):
            img1 = Image.open(dev1_path)
            ctk_img1 = ctk.CTkImage(light_image=img1, dark_image=img1, size=(160, 160))
            ctk.CTkLabel(photo1_frame, image=ctk_img1, text="").pack(expand=True)
        else:
            ctk.CTkLabel(photo1_frame, text="DEV 1\nPHOTO", font=("Helvetica", 16, "bold"), text_color="#000000").pack(expand=True)
            
        # Details
        info1 = ctk.CTkFrame(card1, fg_color="#FFFFFF", border_width=3, border_color="#000000", corner_radius=0)
        info1.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(info1, text="NAME: Ivan Lawrence F Gonzales", font=("Helvetica", 14, "bold"), text_color="#000000", anchor="w").pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(info1, text="ROLE: Lead Software Engineer", font=("Helvetica", 12, "bold"), text_color="#0055FF", anchor="w").pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(info1, text="SYSTEM: MATLAB, PYTHON UI", font=("Helvetica", 11), text_color="#333333", anchor="w").pack(fill="x", padx=12, pady=(2, 8))
        
        # Status Tag
        tag1 = ctk.CTkLabel(card1, text="[ SYSTEM ARCHITECT ]", font=("Helvetica", 11, "bold"), text_color="#000000", fg_color="#FFDC00", corner_radius=0)
        tag1.pack(pady=(0, 10))

        # --- ID CARD 2: UI/UX Designer ---
        card2 = ctk.CTkFrame(
            id_container, 
            fg_color="#F5F5F0", 
            border_width=4, 
            border_color="#000000", 
            corner_radius=0, 
            width=360, 
            height=490
        )
        card2.grid(row=0, column=1, padx=25, pady=10)
        card2.pack_propagate(False)
        
        # Header strip
        c2_head = ctk.CTkFrame(card2, fg_color="#FFDC00", border_width=0, corner_radius=0, height=42)
        c2_head.pack(fill="x")
        c2_head.pack_propagate(False)
        ctk.CTkLabel(c2_head, text="NU LAGUNA", font=("Helvetica", 14, "bold"), text_color="#000000").pack(expand=True)
        
        # Photo Frame
        photo2_frame = ctk.CTkFrame(card2, fg_color="#FFFFFF", border_width=3, border_color="#000000", corner_radius=0, width=170, height=170)
        photo2_frame.pack(pady=18)
        photo2_frame.pack_propagate(False)
        
        if os.path.exists(dev2_path):
            img2 = Image.open(dev2_path)
            ctk_img2 = ctk.CTkImage(light_image=img2, dark_image=img2, size=(160, 160))
            ctk.CTkLabel(photo2_frame, image=ctk_img2, text="").pack(expand=True)
        else:
            ctk.CTkLabel(photo2_frame, text="DEV 2\nPHOTO", font=("Helvetica", 16, "bold"), text_color="#000000").pack(expand=True)
            
        # Details
        info2 = ctk.CTkFrame(card2, fg_color="#FFFFFF", border_width=3, border_color="#000000", corner_radius=0)
        info2.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(info2, text="NAME: Steven Lo Nieva", font=("Helvetica", 14, "bold"), text_color="#000000", anchor="w").pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(info2, text="ROLE: Co UI / UX Designer", font=("Helvetica", 12, "bold"), text_color="#FF3333", anchor="w").pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(info2, text="SYSTEM: Neobrutalism Visuals & OS", font=("Helvetica", 11), text_color="#333333", anchor="w").pack(fill="x", padx=12, pady=(2, 8))
        
        # Status Tag
        tag2 = ctk.CTkLabel(card2, text="[ CREATIVES ]", font=("Helvetica", 11, "bold"), text_color="#FFFFFF", fg_color="#FF3333", corner_radius=0)
        tag2.pack(pady=(0, 10))

        # --- MATLAB ENGINE DESCRIPTION ---
        engine_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        engine_frame.grid(row=2, column=0, pady=(10, 30), padx=40, sticky="ew")
        
        ctk.CTkLabel(
            engine_frame, 
            text="⚙️ HERTZ2HERTZ ENGINE: PYTHON WITH MATLAB ENGINE", 
            font=("Helvetica", 14, "bold"), 
            text_color="#000000"
        ).pack(pady=(15, 5))
        
        desc = "It is a matlab calculator with python thinter UI"
        ctk.CTkLabel(
            engine_frame, 
            text=desc, 
            font=("Helvetica", 12), 
            text_color="#333333", 
            wraplength=700, 
            justify="center"
        ).pack(pady=(0, 15), padx=20)

        # ENGINE PHOTO
        engine_photo_path = os.path.join(base_dir, "assets", "engine_photo.png")
        if os.path.exists(engine_photo_path):
            img_engine = Image.open(engine_photo_path)
            # Scale proportionally based on width of 400
            width, height = img_engine.size
            new_width = 300
            new_height = int(height * (new_width / width))
            ctk_img_engine = ctk.CTkImage(light_image=img_engine, dark_image=img_engine, size=(new_width, new_height))
            
            # Neobrutalist border wrapper
            img_wrapper = ctk.CTkFrame(engine_frame, fg_color="#000000", border_width=4, border_color="#000000", corner_radius=0)
            img_wrapper.pack(pady=(0, 20))
            ctk.CTkLabel(img_wrapper, image=ctk_img_engine, text="").pack(padx=2, pady=2)
