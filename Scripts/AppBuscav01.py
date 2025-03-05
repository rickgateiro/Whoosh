import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime
import re
from difflib import get_close_matches
import json

class PDFProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Processor")
        self.root.geometry("800x600")
        
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
        ttk.Button(self.import_frame, text="Processar PDFs", 
                  command=self.process_pdfs, style='primary.TButton').pack(pady=20)
        
        # Log area
        log_frame = ttk.LabelFrame(self.import_frame, text="Log", padding=10)
        log_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = ttk.Text(log_frame, height=10)
        self.log_text.pack(fill=BOTH, expand=True)

    def setup_search_tab(self):
        # Search input
        search_frame = ttk.Frame(self.search_frame)
        search_frame.pack(fill=X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        ttk.Button(search_frame, text="Buscar", 
                  command=self.search_documents, style='primary.TButton').pack(side=LEFT, padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(self.search_frame, text="Resultados", padding=10)
        results_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = ttk.Text(results_frame, height=10)
        self.results_text.pack(fill=BOTH, expand=True)

    def select_directory(self):
        directory = ttk.filedialog.askdirectory(
            initialdir="c:\\Dev\\Whoosh\\pdf",
            title="Selecione o diretório com PDFs"
        )
        if directory:
            self.dir_entry.delete(0, END)
            self.dir_entry.insert(0, directory)

    def process_pdfs(self):
        # Implementation will be added later
        self.log_text.insert(END, "Processando PDFs...\n")
        self.log_text.see(END)

    def search_documents(self):
        # Implementation will be added later
        self.results_text.insert(END, "Realizando busca...\n")
        self.results_text.see(END)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = PDFProcessorGUI(root)
    root.mainloop()