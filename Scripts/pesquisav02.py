import os
import json
import csv
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Configurar Poppler
os.environ['PATH'] += r';C:\poppler-24.08.0\Library\bin'

def extract_text_from_pdf(pdf_path):
    # Converte o PDF em uma lista de imagens
    pages = convert_from_path(pdf_path, dpi=300)
    
    # Estrutura para armazenar as informações
    pdf_data = {
        "document_info": {
            "filename": os.path.basename(pdf_path),
            "path": pdf_path,
            "extraction_date": datetime.now().isoformat(),
            "total_pages": len(pages)
        },
        "pages": []
    }
    
    # Extrai o texto de cada página
    for i, page in enumerate(pages):
        page_text = pytesseract.image_to_string(page, lang='por')
        
        # Adiciona informações da página ao JSON
        page_data = {
            "page_number": i + 1,
            "content": page_text.strip(),
            "word_count": len(page_text.split())
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
    # Caminho do PDF
    pdf_path = "pdf/exemplo.pdf"
    
    # Extrai o texto e cria a estrutura JSON
    pdf_data = extract_text_from_pdf(pdf_path)
    
    # Define o nome base (sem extensão) para os arquivos de saída
    base_name = os.path.splitext(pdf_path)[0]
    
    # Salva os dados em diferentes formatos
    json_file = save_to_json(pdf_data, base_name)
    csv_file = save_to_csv(pdf_data, base_name)
    txt_file = save_to_txt(pdf_data, base_name)
    
    print(f"OCR extraction completed. Files saved as:")
    print(f"JSON: {json_file}")
    print(f"CSV: {csv_file}")
    print(f"TXT: {txt_file}")