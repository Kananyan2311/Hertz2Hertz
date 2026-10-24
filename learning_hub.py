import customtkinter as ctk
import os
import fitz  # PyMuPDF
from PIL import Image
from retro_ui import RETRO_FONT, TITLE_FONT

class LearningHub(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # Colorful Sidebar Menu - Widened to 320px to prevent text clipping
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color="#F5F5F0", border_width=4, border_color="#000000")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.sidebar, text=" 📚 STUDY HUB ", font=TITLE_FONT, text_color="#000000", fg_color="#FEF08A").grid(row=0, column=0, padx=10, pady=15, sticky="ew")

        # Scrollable list of topics
        self.topic_list = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.topic_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=5)
        self.topic_buttons = {}

        # PDF Viewing State
        self.current_doc = None
        self.current_page = 0
        self.active_pdf_path = None
        
        # Main content area (PDF Viewer)
        self.content_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=4, border_color="#000000", corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        
        # Toolbar
        self.toolbar = ctk.CTkFrame(self.content_frame, fg_color="#FFDC00", height=50, corner_radius=0, border_width=4, border_color="#000000")
        self.toolbar.grid(row=0, column=0, sticky="ew")
        
        self.btn_prev = ctk.CTkButton(self.toolbar, text="< Prev", font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_width=3, border_color="#000000", corner_radius=0, command=self.prev_page, width=80)
        self.btn_prev.pack(side="left", padx=10, pady=5)
        
        self.lbl_page = ctk.CTkLabel(self.toolbar, text="Page - / -", font=RETRO_FONT, text_color="#000000")
        self.lbl_page.pack(side="left", padx=10, pady=5)
        
        self.btn_next = ctk.CTkButton(self.toolbar, text="Next >", font=RETRO_FONT, fg_color="#FFFFFF", text_color="#000000", border_width=3, border_color="#000000", corner_radius=0, command=self.next_page, width=80)
        self.btn_next.pack(side="left", padx=10, pady=5)
        
        self.lbl_title = ctk.CTkLabel(self.toolbar, text="No PDF Selected", font=RETRO_FONT, text_color="#000000")
        self.lbl_title.pack(side="right", padx=20, pady=5)
        
        # Canvas for Image
        self.lbl_pdf = ctk.CTkLabel(self.content_frame, text="Select a PDF from the sidebar to view.", font=TITLE_FONT, text_color="#000000")
        self.lbl_pdf.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.load_pdfs()

    def load_pdfs(self):
        base_dir = "pdfs"
        categories = ["electronics", "logic"]
        
        for cat in categories:
            cat_path = os.path.join(base_dir, cat)
            if not os.path.exists(cat_path):
                continue
                
            # Category Header
            cat_lbl = ctk.CTkLabel(
                self.topic_list, 
                text=f"📁 {cat.upper()}", 
                font=("Helvetica", 13, "bold"), 
                text_color="#000000", 
                fg_color="#FEF08A"
            )
            cat_lbl.pack(fill="x", pady=(12, 6))
            
            # List PDFs
            for f in sorted(os.listdir(cat_path)):
                if f.lower().endswith(".pdf"):
                    clean_name = f.replace(".pdf", "").replace("_", " ").replace("ECELXC30-", "").replace("ECELXC30 ", "")
                    # Compact display label
                    btn = ctk.CTkButton(
                        self.topic_list, 
                        text=clean_name, 
                        font=("Helvetica", 10, "bold"), 
                        fg_color="#FFFFFF", 
                        text_color="#000000", 
                        border_width=3, 
                        border_color="#000000", 
                        corner_radius=0, 
                        hover_color="#BAE6FD", 
                        anchor="w",
                        command=lambda path=os.path.join(cat_path, f), name=clean_name: self.open_pdf(path, name)
                    )
                    btn.pack(fill="x", pady=3, padx=2)
                    self.topic_buttons[os.path.join(cat_path, f)] = btn

    def open_pdf(self, path, name):
        if self.current_doc:
            self.current_doc.close()
            
        try:
            self.current_doc = fitz.open(path)
            self.current_page = 0
            self.active_pdf_path = path
            self.lbl_title.configure(text=f"📄 {name}")
            
            # Highlight selected PDF button
            for p, b in self.topic_buttons.items():
                if p == path:
                    b.configure(fg_color="#FEF08A", border_color="#000000", text_color="#000000")
                else:
                    b.configure(fg_color="#FFFFFF", border_color="#000000", text_color="#000000")
                    
            self.render_page()
        except Exception as e:
            self.lbl_pdf.configure(text=f"Error loading PDF:\n{e}", image=None)

    def render_page(self):
        if not self.current_doc: return
        
        try:
            page = self.current_doc[self.current_page]
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0)) # 2x zoom for clarity
            mode = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            
            # Resize image to fit label if necessary, but CTkImage handles scaling well if we provide size
            # Calculate aspect ratio preserving size based on typical window size (e.g. max height 700)
            target_height = 650
            ratio = target_height / img.height
            target_width = int(img.width * ratio)
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_width, target_height))
            self.lbl_pdf.configure(image=ctk_img, text="")
            
            self.lbl_page.configure(text=f"Page {self.current_page + 1} / {len(self.current_doc)}")
        except Exception as e:
            self.lbl_pdf.configure(text=f"Error rendering page:\n{e}", image=None)

    def next_page(self):
        if self.current_doc and self.current_page < len(self.current_doc) - 1:
            self.current_page += 1
            self.render_page()
            
    def prev_page(self):
        if self.current_doc and self.current_page > 0:
            self.current_page -= 1
            self.render_page()

