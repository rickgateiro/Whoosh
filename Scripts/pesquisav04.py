import os
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime
import re
from difflib import get_close_matches

# Configure Tesseract and Poppler
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
os.environ['PATH'] += r';C:\poppler-24.08.0\Library\bin'

def load_portuguese_dictionary():
    try:
        with open('c:\\Dev\\Whoosh\\portuguese_words.txt', 'r', encoding='utf-8') as f:
            return {word.strip().lower() for word in f if len(word.strip()) > 1}
    except FileNotFoundError:
        print("Dictionary file not found!")
        return set()

def find_similar_words(word, dictionary, cutoff=0.8):
    return get_close_matches(word, dictionary, n=1, cutoff=cutoff)

def split_compound_words(word, dictionary):
    # Try to split compound words based on dictionary entries
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
    
    # First, split text into potential words
    words = re.findall(r'\b[a-záàâãéêíóôõúüç]+\b', text, re.IGNORECASE)
    
    valid_words = []
    for word in words:
        # Skip single letters
        if len(word) <= 1:
            continue
        
        # If it's a compound word, try to split it
        if len(word) > 12:  # Likely a compound word
            split_words = split_compound_words(word, dictionary)
            if split_words:
                valid_words.extend(split_words)
                continue
        
        # Check if word exists in dictionary
        if word in dictionary:
            valid_words.append(word)
    
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
        
        # Only add pages with valid content
        if cleaned_text.strip():
            page_data = {
                "page_number": i + 1,
                "content": cleaned_text,
                "word_count": len(cleaned_text.split())
            }
            pdf_data["pages"].append(page_data)
    
    return pdf_data

# Commented out JSON and CSV functions
"""
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
"""

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
    txt_file = save_to_txt(pdf_data, base_name)
    
    print(f"OCR extraction completed. File saved as:")
    print(f"TXT: {txt_file}")