import os
import json
import fitz
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser
import unidecode
import re

def clean_text(text):
    # Convert to lowercase and remove accents
    text = unidecode.unidecode(text.lower())
    
    # Simple word tokenization using regex
    words = re.findall(r'\b\w+\b', text)
    
    # Clean and filter words
    cleaned_words = []
    for word in words:
        # Remove special characters and numbers
        word = re.sub(r'[^a-zA-Z\s]', '', word)
        
        # Keep words longer than 2 characters
        if word and len(word) > 2:
            cleaned_words.append(word)
    
    return ' '.join(cleaned_words)

def create_searchable_index(txt_path, pdf_path):
    schema = Schema(
        content=TEXT(stored=True),
        page_number=NUMERIC(stored=True),
        pdf_path=ID(stored=True)
    )
    
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        current_page = None
        current_content = []
        
        for line in f:
            if line.startswith('Page '):
                if current_page is not None and current_content:
                    cleaned_content = clean_text('\n'.join(current_content))
                    writer.add_document(
                        content=cleaned_content,
                        page_number=current_page,
                        pdf_path=pdf_path
                    )
                current_page = int(line.split()[1])
                current_content = []
            else:
                current_content.append(line.strip())
    
    if current_page is not None and current_content:
        cleaned_content = clean_text('\n'.join(current_content))
        writer.add_document(
            content=cleaned_content,
            page_number=current_page,
            pdf_path=pdf_path
        )
    
    writer.commit()
    return ix

def search_and_show_pdf(query_text, index):
    with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse(query_text)
        results = searcher.search(query, limit=10)
        
        if not results:
            print(f"No results found for '{query_text}'")
            return
        
        pdf_path = results[0]['pdf_path']
        doc = fitz.open(pdf_path)
        
        for hit in results:
            page_num = hit['page_number']
            print(f"\nFound in page {page_num}:")
            print(f"Context: {hit.highlights('content')}\n")
            
            page = doc.load_page(page_num - 1)
            text_instances = page.search_for(query_text)
            for inst in text_instances:
                annot = page.add_highlight_annot(inst)
                annot.set_colors({"stroke": (1, 1, 0), "fill": (1, 1, 0.3)})
                annot.set_opacity(0.5)
                annot.update()
        
        temp_pdf = "search_result_temp.pdf"
        doc.save(temp_pdf)
        doc.close()
        print(f"\nHighlighted PDF saved as: {temp_pdf}")

if __name__ == "__main__":
    txt_path = "c:\\Dev\\Whoosh\\pdf\\exemplo.txt"
    pdf_path = "c:\\Dev\\Whoosh\\pdf\\exemplo.pdf"
    
    # Create search index with cleaned text
    index = create_searchable_index(txt_path, pdf_path)
    
    # Example search
    search_term = input("Enter search term: ")
    search_and_show_pdf(search_term, index)