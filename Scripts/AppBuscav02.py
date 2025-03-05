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

class PDFProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Processor")
        self.root.geometry("800x600")
        
        # Configure Tesseract and Poppler
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
        os.environ['PATH'] += r';C:\poppler-24.08.0\Library\bin'
        
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

    def log_message(self, message):
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)

    def start_processing(self):
        self.process_button.configure(state='disabled')
        self.progress.start()
        self.log_message("Iniciando processamento...")
        
        # Start processing in a separate thread
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
        except Exception as e:
            self.log_message(f"Erro: {str(e)}")
        finally:
            # Re-enable button and stop progress bar
            self.root.after(0, self.finish_processing)

    def finish_processing(self):
        self.process_button.configure(state='normal')
        self.progress.stop()

    def search_documents(self):
        # Implementation will be added later
        self.results_text.insert(END, "Realizando busca...\n")
        self.results_text.see(END)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = PDFProcessorGUI(root)
    root.mainloop()