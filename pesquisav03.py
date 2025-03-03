import os
import json
import csv
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime
import re

# Configurar Tesseract e Poppler
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
os.environ['PATH'] += r';C:\poppler-24.08.0\Library\bin'

def load_portuguese_dictionary():
    try:
        with open('c:\\Dev\\Whoosh\\dicionarioptbr.txt', 'r', encoding='utf-8') as f:
            return {word.strip().lower() for word in f}
    except FileNotFoundError:
        print("Dictionary file not found!")
        return set()

def clean_text(text, dictionary):
    # Convert to lowercase
    text = text.lower()
    
    # Split into words (considering Portuguese characters)
    words = re.findall(r'\b[a-záàâãéêíóôõúüç]+\b', text, re.IGNORECASE)
    
    # Keep only words that exist in the dictionary
    valid_words = [word for word in words if word in dictionary]
    
    return ' '.join(valid_words)

def extract_text_from_pdf(pdf_path):
    dictionary = load_portuguese_dictionary()
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
        cleaned_text = clean_text(raw_text, dictionary)
        
        # Only add pages with valid content
        if cleaned_text.strip():
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
    pdf_path = "c:\\Dev\\Whoosh\\pdf\\exemplo.pdf"
    base_name = os.path.splitext(pdf_path)[0]
    
    pdf_data = extract_text_from_pdf(pdf_path)
    
    json_file = save_to_json(pdf_data, base_name)
    csv_file = save_to_csv(pdf_data, base_name)
    txt_file = save_to_txt(pdf_data, base_name)
    
    print(f"OCR extraction completed. Files saved as:")
    print(f"JSON: {json_file}")
    print(f"CSV: {csv_file}")
    print(f"TXT: {txt_file}")