import os
import json
import csv
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime
import unidecode
import re

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Configurar Poppler
os.environ['PATH'] += r';C:\poppler-24.08.0\Library\bin'

def load_portuguese_dictionary():
    try:
        with open('portuguese_words.txt', 'r', encoding='utf-8') as f:
            return set(word.strip().lower() for word in f)
    except FileNotFoundError:
        # If dictionary file not found, return empty set
        return set()

def clean_text(text, portuguese_words):
    # Convert to lowercase and remove accents
    text = unidecode.unidecode(text.lower())
    
    # Split into words and clean
    words = re.findall(r'\b\w+\b', text)
    cleaned_words = []
    
    for word in words:
        # Remove special characters and numbers
        word = re.sub(r'[^a-zA-Z\s]', '', word)
        
        # Keep words that are in Portuguese dictionary or longer than 2 characters
        if word and (word.lower() in portuguese_words or len(word) > 2):
            cleaned_words.append(word)
    
    # Reconstruct text with cleaned words
    cleaned_text = ' '.join(cleaned_words)
    
    # Remove multiple spaces and clean up
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

def extract_text_from_pdf(pdf_path, portuguese_words):
    pages = convert_from_path(pdf_path, dpi=300)
    
    pdf_data = {
        "document_info": {
            "filename": os.path.basename(pdf_path),
            "path": pdf_path,
            "extraction_date": datetime.now().isoformat(),
            "total_pages": len(pages)
        },
        "pages": []
    }
    
    for i, page in enumerate(pages):
        # Extract text and clean it
        raw_text = pytesseract.image_to_string(page, lang='por')
        cleaned_text = clean_text(raw_text, portuguese_words)
        
        page_data = {
            "page_number": i + 1,
            "content": cleaned_text,
            "word_count": len(cleaned_text.split())
        }
        pdf_data["pages"].append(page_data)
    
    return pdf_data

def save_to_json(data, base_name):
    json_path = f"{base_name}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return json_path

def save_to_csv(data, base_name):
    csv_path = f"{base_name}.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Page Number', 'Word Count', 'Content'])
        for page in data['pages']:
            writer.writerow([
                page['page_number'],
                page['word_count'],
                page['content']
            ])
    return csv_path

def save_to_txt(data, base_name):
    txt_path = f"{base_name}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Document: {data['document_info']['filename']}\n")
        f.write(f"Extraction Date: {data['document_info']['extraction_date']}\n")
        f.write("-" * 80 + "\n\n")
        
        for page in data['pages']:
            f.write(f"Page {page['page_number']}\n")
            f.write("-" * 40 + "\n")
            f.write(page['content'])
            f.write("\n\n")
    return txt_path

if __name__ == "__main__":
    # Load Portuguese dictionary
    portuguese_words = load_portuguese_dictionary()
    
    # Caminho do PDF
    pdf_path = "c:\\Dev\\Whoosh\\pdf\\exemplo.pdf"
    
    # Extrai o texto e cria a estrutura JSON
    pdf_data = extract_text_from_pdf(pdf_path, portuguese_words)
    
    # Define o nome base (sem extensão) para os arquivos de saída
    base_name = os.path.splitext(pdf_path)[0]
    
    # Salva os dados em diferentes formatos (sobrescrevendo se existirem)
    json_file = save_to_json(pdf_data, base_name)
    csv_file = save_to_csv(pdf_data, base_name)
    txt_file = save_to_txt(pdf_data, base_name)
    
    print(f"OCR extraction completed. Files saved as:")
    print(f"JSON: {json_file}")
    print(f"CSV: {csv_file}")
    print(f"TXT: {txt_file}")