import os
import json
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime
import re
from difflib import get_close_matches

# funcionando  e criando o json e o txt

# Configure Tesseract and Poppler
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
os.environ['PATH'] += r';C:\poppler-24.08.0\Library\bin'

def load_portuguese_dictionary():
    try:
        with open('c:\\Dev\\Whoosh\\portuguese_words.txt', 'r', encoding='utf-8') as f:
            return {word.strip().lower() for word in f if len(word.strip()) > 2}  # Minimum 3 characters
    except FileNotFoundError:
        print("Dictionary file not found!")
        return set()

def find_similar_words(word, dictionary, cutoff=0.85):  # Increased similarity threshold
    return get_close_matches(word, dictionary, n=1, cutoff=cutoff)

def split_compound_words(word, dictionary):
    words = []
    current = ""
    for char in word.lower():
        current += char
        remaining = word[len(current):].lower()
        
        if current in dictionary:
            if not remaining or any(remaining.startswith(w) for w in dictionary):
                words.append(current)
                current = ""
    
    if current and current in dictionary:
        words.append(current)
    
    return words if words else []

def clean_text(text, dictionary):
    # Convert to lowercase
    text = text.lower()
    
    # Split into words (considering Portuguese characters)
    words = re.findall(r'\b[a-záàâãéêíóôõúüç]+\b', text, re.IGNORECASE)
    
    valid_words = []
    for word in words:
        # Skip short words
        if len(word) <= 2:
            continue
        
        # Try to split compound words
        if len(word) > 12:
            split_words = split_compound_words(word, dictionary)
            if split_words:
                valid_words.extend(split_words)
                continue
        
        # Check for exact matches
        if word in dictionary:
            valid_words.append(word)
            continue
        
        # Try to find similar words
        similar = find_similar_words(word, dictionary)
        if similar:
            valid_words.append(similar[0])
    
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
        raw_text = pytesseract.image_to_string(page, lang='por')
        cleaned_text = clean_text(raw_text, dictionary)
        
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
    pdf_directory = "c:\\Dev\\Whoosh\\pdf"
    
    for pdf_file in os.listdir(pdf_directory):
        if pdf_file.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_directory, pdf_file)
            base_name = os.path.splitext(pdf_path)[0]
            
            print(f"Processing: {pdf_file}")
            try:
                pdf_data = extract_text_from_pdf(pdf_path)
                txt_file = save_to_txt(pdf_data, base_name)
                json_file = save_to_json(pdf_data, base_name)
                print(f"Created TXT: {txt_file}")
                print(f"Created JSON: {json_file}")
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
    
    print("Processing completed!")