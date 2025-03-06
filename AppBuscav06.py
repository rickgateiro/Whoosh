# Version: 6.0
# Date: 2024-03-05
# Changes: Replaced dual file lists with dropdown menu for file type selection

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime
import re
from difflib import get_close_matches
import json
import threading
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io

class PDFProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Processador de PDF")
        self.root.geometry("1024x768")
        
        # Configure Tesseract and Poppler
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
        os.environ['PATH'] += r';C:\poppler-24.08.0\Library\bin'
        
        # PDF viewer variables
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Create Import tab
        self.import_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.import_frame, text="Importação")
        self.setup_import_tab()
        
        # Create Search tab
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Pesquisa")
        self.setup_search_tab()
        
        # Create View tab
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="Visualização")
        self.setup_view_tab()

    def setup_import_tab(self):
        # Directory selection
        dir_frame = ttk.Frame(self.import_frame)
        dir_frame.pack(fill=X, padx=5, pady=5)
        
        ttk.Label(dir_frame, text="Diretório PDF:").pack(side=LEFT, padx=5)
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.dir_entry.insert(0, "c:\\Dev\\Whoosh\\pdf")
        
        ttk.Button(dir_frame, text="Selecionar", command=self.select_directory).pack(side=LEFT, padx=5)
        
        # Process button
        self.process_button = ttk.Button(self.import_frame, text="Processar PDFs", 
                                       command=self.start_processing, style='primary.TButton')
        self.process_button.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.import_frame, mode='indeterminate')
        self.progress.pack(fill=X, padx=5, pady=5)
        
        # Log area
        log_frame = ttk.LabelFrame(self.import_frame, text="Log", padding=10)
        log_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = ttk.Text(log_frame, height=10)
        self.log_text.pack(fill=BOTH, expand=True)

    def setup_search_tab(self):
        # Create main container
        main_container = ttk.Frame(self.search_frame)
        main_container.pack(fill=BOTH, expand=True)
        
        # Create file list panel (left side)
        files_frame = ttk.LabelFrame(main_container, text="Arquivos Disponíveis", padding=10)
        files_frame.pack(side=LEFT, fill=Y, padx=5, pady=5)
        
        # File type dropdown
        ttk.Label(files_frame, text="Tipo de Arquivo:").pack(anchor=W, padx=5, pady=2)
        self.search_file_type = ttk.Combobox(files_frame, values=["JSON", "TXT"], state="readonly")
        self.search_file_type.pack(fill=X, padx=5, pady=5)
        self.search_file_type.set("JSON")
        self.search_file_type.bind('<<ComboboxSelected>>', self.update_search_file_list)
        
        # Files List
        self.search_files_list = ttk.Treeview(files_frame, selectmode="browse", show="tree", height=15)
        self.search_files_list.pack(fill=X, padx=5, pady=5)
        
        # Refresh button
        ttk.Button(files_frame, text="Atualizar Lista", 
                  command=self.update_search_file_list).pack(pady=5)
        
        # Create search and results panel (right side)
        search_container = ttk.Frame(main_container)
        search_container.pack(side=LEFT, fill=BOTH, expand=True, padx=5)
        
        # Search input
        search_frame = ttk.LabelFrame(search_container, text="Pesquisa", padding=10)
        search_frame.pack(fill=X, pady=5)
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=X)
        
        ttk.Label(search_input_frame, text="Termo:").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_input_frame)
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        ttk.Button(search_input_frame, text="Buscar", 
                  command=self.search_documents, 
                  style='primary.TButton').pack(side=LEFT, padx=5)
        
        # PDF viewer area
        viewer_frame = ttk.LabelFrame(search_container, text="Visualizador PDF", padding=10)
        viewer_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(viewer_frame)
        nav_frame.pack(fill=X, pady=5)
        
        ttk.Button(nav_frame, text="Anterior", 
                  command=self.prev_page).pack(side=LEFT, padx=5)
        ttk.Button(nav_frame, text="Próxima", 
                  command=self.next_page).pack(side=LEFT, padx=5)
        
        self.page_label = ttk.Label(nav_frame, text="Página: 0/0")
        self.page_label.pack(side=LEFT, padx=5)
        
        # Zoom buttons
        ttk.Button(nav_frame, text="Zoom +", 
                  command=self.zoom_in).pack(side=RIGHT, padx=5)
        ttk.Button(nav_frame, text="Zoom -", 
                  command=self.zoom_out).pack(side=RIGHT, padx=5)
        
        # PDF display
        self.pdf_canvas = ttk.Canvas(viewer_frame, bg='white')
        self.pdf_canvas.pack(fill=BOTH, expand=True)

    def setup_view_tab(self):
        # Create main container
        main_container = ttk.Frame(self.view_frame)
        main_container.pack(fill=BOTH, expand=True)
        
        # Create file list panel (left side)
        files_frame = ttk.LabelFrame(main_container, text="Arquivos Disponíveis", padding=10)
        files_frame.pack(side=LEFT, fill=Y, padx=5, pady=5)
        
        # File type dropdown
        ttk.Label(files_frame, text="Tipo de Arquivo:").pack(anchor=W, padx=5, pady=2)
        self.view_file_type = ttk.Combobox(files_frame, values=["JSON", "TXT"], state="readonly")
        self.view_file_type.pack(fill=X, padx=5, pady=5)
        self.view_file_type.set("JSON")
        self.view_file_type.bind('<<ComboboxSelected>>', self.update_view_file_list)
        
        # Files List
        self.view_files_list = ttk.Treeview(files_frame, selectmode="browse", show="tree", height=15)
        self.view_files_list.pack(fill=X, padx=5, pady=5)
        self.view_files_list.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # Refresh button
        ttk.Button(files_frame, text="Atualizar Lista", 
                  command=self.update_view_file_list).pack(pady=5)
        
        # Create content panel (right side)
        content_container = ttk.Frame(main_container)
        content_container.pack(side=LEFT, fill=BOTH, expand=True, padx=5)
        
        # Content area with scrollbar
        content_frame = ttk.LabelFrame(content_container, text="Conteúdo do Arquivo", padding=10)
        content_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.content_text = ttk.Text(content_frame, height=10, yscrollcommand=scrollbar.set)
        self.content_text.pack(fill=BOTH, expand=True)
        scrollbar.config(command=self.content_text.yview)

    def update_search_file_list(self, event=None):
        self.search_files_list.delete(*self.search_files_list.get_children())
        file_type = self.search_file_type.get().lower()
        
        directory = self.dir_entry.get()
        for file in os.listdir(directory):
            if file.endswith(f'.{file_type}'):
                self.search_files_list.insert('', 'end', text=file)

    def update_view_file_list(self, event=None):
        self.view_files_list.delete(*self.view_files_list.get_children())
        file_type = self.view_file_type.get().lower()
        
        directory = self.dir_entry.get()
        for file in os.listdir(directory):
            if file.endswith(f'.{file_type}'):
                self.view_files_list.insert('', 'end', text=file)

    def on_file_select(self, event):
        self.content_text.delete(1.0, END)
        
        selection = self.view_files_list.selection()
        if not selection:
            return
            
        filename = self.view_files_list.item(selection[0])['text']
        filepath = os.path.join(self.dir_entry.get(), filename)
        
        try:
            if filename.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.content_text.insert(END, f"Arquivo: {data['document_info']['filename']}\n")
                    self.content_text.insert(END, f"Data de Extração: {data['document_info']['extraction_date']}\n")
                    self.content_text.insert(END, f"Total de Páginas: {data['document_info']['total_pages']}\n\n")
                    
                    for page in data['pages']:
                        self.content_text.insert(END, f"Página {page['page_number']}\n")
                        self.content_text.insert(END, f"Palavras: {page['word_count']}\n")
                        self.content_text.insert(END, f"Conteúdo:\n{page['content']}\n")
                        self.content_text.insert(END, "-" * 50 + "\n\n")
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.content_text.insert(END, content)
        except Exception as e:
            self.content_text.insert(END, f"Erro ao ler arquivo: {str(e)}")

    def select_directory(self):
        directory = ttk.filedialog.askdirectory(
            initialdir="c:\\Dev\\Whoosh\\pdf",
            title="Selecione o diretório com PDFs"
        )
        if directory:
            self.dir_entry.delete(0, END)
            self.dir_entry.insert(0, directory)
            self.update_search_file_list()
            self.update_view_file_list()

    def log_message(self, message):
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)

    def start_processing(self):
        self.process_button.configure(state='disabled')
        self.progress.start()
        self.log_message("Iniciando processamento...")
        
        thread = threading.Thread(target=self.process_pdfs)
        thread.daemon = True
        thread.start()

    def process_pdfs(self):
        try:
            from pesquisav06 import load_portuguese_dictionary, clean_text, extract_text_from_pdf, save_to_json, save_to_txt
            
            pdf_directory = self.dir_entry.get()
            
            for pdf_file in os.listdir(pdf_directory):
                if pdf_file.lower().endswith('.pdf'):
                    pdf_path = os.path.join(pdf_directory, pdf_file)
                    base_name = os.path.splitext(pdf_path)[0]
                    
                    self.log_message(f"Processando: {pdf_file}")
                    try:
                        pdf_data = extract_text_from_pdf(pdf_path)
                        txt_file = save_to_txt(pdf_data, base_name)
                        json_file = save_to_json(pdf_data, base_name)
                        self.log_message(f"Criado: {txt_file}")
                        self.log_message(f"Criado: {json_file}")
                    except Exception as e:
                        self.log_message(f"Erro ao processar {pdf_file}: {str(e)}")
            
            self.log_message("Processamento concluído!")
            self.update_search_file_list()
            self.update_view_file_list()
        except Exception as e:
            self.log_message(f"Erro: {str(e)}")
        finally:
            self.root.after(0, self.finish_processing)

    def finish_processing(self):
        self.process_button.configure(state='normal')
        self.progress.stop()

    def search_documents(self):
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            return

        selected = self.search_files_list.selection()
        if not selected:
            return

        filename = self.search_files_list.item(selected[0])['text']
        pdf_filename = filename.replace('.json', '.pdf')
        pdf_path = os.path.join(self.dir_entry.get(), pdf_filename)

        try:
            self.current_pdf = fitz.open(pdf_path)
            self.total_pages = len(self.current_pdf)
            self.current_page = 0
            
            # Search and highlight
            for page_num in range(self.total_pages):
                page = self.current_pdf[page_num]
                text_instances = page.search_for(search_term)
                
                # Highlight each occurrence
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=(1, 0, 0))  # Red color
                    highlight.update()
            
            self.display_current_page()
            
        except Exception as e:
            self.log_message(f"Erro ao processar PDF: {str(e)}")

    def display_current_page(self):
        if not self.current_pdf:
            return
            
        page = self.current_pdf[self.current_page]
        pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_factor, self.zoom_factor))
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        photo = ImageTk.PhotoImage(img)
        
        # Update canvas
        self.pdf_canvas.delete("all")
        self.pdf_canvas.config(width=pix.width, height=pix.height)
        self.pdf_canvas.create_image(0, 0, anchor=NW, image=photo)
        self.pdf_canvas.image = photo  # Keep reference
        
        self.page_label.config(text=f"Página: {self.current_page + 1}/{self.total_pages}")

    def next_page(self):
        if self.current_pdf and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_current_page()

    def prev_page(self):
        if self.current_pdf and self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.display_current_page()

    def zoom_out(self):
        self.zoom_factor *= 0.8
        self.display_current_page()

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = PDFProcessorGUI(root)
    root.mainloop()